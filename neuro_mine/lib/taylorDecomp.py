"""
Module for decomposing the prediction ANN into piecewise linear functions
via Taylor Series decomposition
"""

import numpy as np
from numba import njit
from typing import List, Tuple
from neuro_mine.lib import utilities
from neuro_mine.lib import model
import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import tensorflow as tf
tf.get_logger().setLevel("ERROR")
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)


@tf.function
def d2ca_dr2(mdl: model.ActivityPredictor, reg_input: np.ndarray) -> Tuple[tf.Tensor, tf.Tensor]:
    x = tf.convert_to_tensor(reg_input)
    with tf.GradientTape() as t2:
        t2.watch(x)
        with tf.GradientTape() as t1:
            t1.watch(x)
            # NOTE: The following is slightly faster than ca = mdl(x) presumably due to skipping of dropout layers
            # However it is not compatible with resizing the model!!
            # c = mdl.conv_layer(x)
            # d1 = mdl.deep_1(mdl.flatten(c))
            # d2 = mdl.deep_2(d1)
            # ca = mdl.out(d2)
            ca = mdl(x)
        jacobian = t1.gradient(ca, x)
    hessian = t2.jacobian(jacobian, x)
    return jacobian, hessian


@tf.function
def d2ca_dr2_batched(mdl: model.ActivityPredictor, reg_input: tf.Tensor) -> Tuple[tf.Tensor, tf.Tensor]:
    """
    Computes Jacobians and Hessians for an entire batch of windows simultaneously.
    """
    x = tf.convert_to_tensor(reg_input)
    with tf.GradientTape() as t2:
        t2.watch(x)
        with tf.GradientTape() as t1:
            t1.watch(x)
            ca = mdl(x)
        jacobian = t1.gradient(ca, x)  # Correctly accumulates independent gradients across the batch

    # FIX: batch_jacobian restricts derivative tracking strictly to matching batch rows
    hessian = t2.batch_jacobian(jacobian, x)
    return jacobian, hessian


@tf.function
def dca_dr(mdl: model.ActivityPredictor, reg_input: np.ndarray) -> tf.Tensor:
    x = tf.convert_to_tensor(reg_input)
    with tf.GradientTape() as t1:
        t1.watch(x)
        # NOTE: The following is slightly faster than ca = mdl(x) presumably due to skipping of dropout layers
        # but not compatible with change layer number in the model
        # c = mdl.conv_layer(x)
        # d1 = mdl.deep_1(mdl.flatten(c))
        # d2 = mdl.deep_2(d1)
        # ca = mdl.out(d2)
        ca = mdl(x)
    jacobian = t1.gradient(ca, x)
    return jacobian


def taylor_predict_batched(mdl: model.ActivityPredictor, regressors: np.ndarray, use_d2: bool, take_every: int,
                           predict_ahead=1, chunk_size=64) -> Tuple[np.ndarray, np.ndarray]:
    if predict_ahead < 1:
        raise ValueError("predict_ahead has to be integer >= 1")

    inp_length = mdl.input_length

    # 1. Generate all current and future window coordinates
    indices = np.arange(inp_length - 1, regressors.shape[0] - predict_ahead, take_every)

    cur_windows = np.array([regressors[i - inp_length + 1: i + 1, :] for i in indices])
    next_windows = np.array([regressors[i - inp_length + 1 + predict_ahead: i + 1 + predict_ahead, :] for i in indices])

    # 2. Batch inference for all actual values
    cur_mod_outs = mdl.get_output(cur_windows)
    next_mod_outs = mdl.get_output(next_windows)

    taylor_predictions = []

    # 3. Process the expensive derivatives in chunk blocks
    for start in range(0, len(indices), chunk_size):
        end = start + chunk_size
        chunk_cur = cur_windows[start:end]
        chunk_next = next_windows[start:end]
        chunk_cur_out = cur_mod_outs[start:end]

        if use_d2:
            # Calls our new batch_jacobian function
            d1_tf, d2_tf = d2ca_dr2_batched(mdl, chunk_cur)

            # Reshape tensors to flat arrays per batch element
            d1_chunk = d1_tf.numpy().reshape(len(chunk_cur), -1)
            d2_chunk = d2_tf.numpy().reshape(len(chunk_cur), d1_chunk.shape[1], d1_chunk.shape[1])
        else:
            d1_tf = dca_dr(mdl, chunk_cur)
            d1_chunk = d1_tf.numpy().reshape(len(chunk_cur), -1)
            d2_chunk = [None] * len(chunk_cur)

        # 4. Compute Taylor expansions for the chunk elements
        for i in range(len(chunk_cur)):
            ann_fix = chunk_cur_out[i]
            d1 = d1_chunk[i]
            d2 = d2_chunk[i]

            tay_pred = _taylor_predict(chunk_cur[i], chunk_next[i], ann_fix, d1, d2)
            taylor_predictions.append(tay_pred)

    return np.array(taylor_predictions), next_mod_outs


def taylor_decompose_batched(mdl: model.ActivityPredictor, regressors: np.ndarray, take_every: int, predict_ahead: int,
                             use_d2=True, chunk_size=64) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Highly optimized, vectorized version of taylor_decompose.
    Eliminates internal Python loops and manual array re-indexing.
    """
    if predict_ahead < 1:
        raise ValueError("predict_ahead has to be integer >= 1")

    inp_length = mdl.input_length
    nregs = regressors.shape[1]

    # 1. Generate window indices for batching
    indices = np.arange(inp_length - 1, regressors.shape[0] - predict_ahead, take_every)

    cur_windows = np.array([regressors[i - inp_length + 1: i + 1, :] for i in indices])
    next_windows = np.array([regressors[i - inp_length + 1 + predict_ahead: i + 1 + predict_ahead, :] for i in indices])

    # 2. Batch inference for all true output changes
    cur_mod_outs = mdl.get_output(cur_windows)
    next_mod_outs = mdl.get_output(next_windows)
    mdl_out_change = next_mod_outs - cur_mod_outs

    full_tp_change = []
    by_reg_tp_change = []

    # 3. Process derivatives and interactions in chunks to protect memory
    for start in range(0, len(indices), chunk_size):
        end = start + chunk_size
        chunk_cur = cur_windows[start:end]
        chunk_next = next_windows[start:end]
        B = chunk_cur.shape[0]

        # Flatten regressor differences per batch element (Shape: B, L*R)
        reg_diff = (chunk_next - chunk_cur).reshape(B, -1)

        if use_d2:
            # Reuses the batched function we built previously!
            d1_tf, d2_tf = d2ca_dr2_batched(mdl, chunk_cur)
            d1 = d1_tf.numpy().reshape(B, -1)
            d2 = d2_tf.numpy().reshape(B, d1.shape[1], d1.shape[1])

            # First order contributions
            taylor_d1 = reg_diff * d1
            summed_d1 = taylor_d1.reshape(B, inp_length, nregs).sum(axis=1)  # Shape: (B, R)

            # Second order contributions (NumPy broadcasting for outer product)
            diff_outer = reg_diff[:, :, None] * reg_diff[:, None, :]  # Shape: (B, L*R, L*R)
            taylor_d2 = 0.5 * diff_outer * d2

            # ARRAY MAGIC: Reshape to separate Time (L) and Regressors (R) dimensions.
            # Summing over the Time axes (1 and 3) natively aggregates interactions by regressor!
            summed_d2 = taylor_d2.reshape(B, inp_length, nregs, inp_length, nregs).sum(axis=(1, 3))  # Shape: (B, R, R)

        else:
            # Standard dca_dr natively calculates batches correctly without modification
            d1_tf = dca_dr(mdl, chunk_cur)
            d1 = d1_tf.numpy().reshape(B, -1)

            taylor_d1 = reg_diff * d1
            summed_d1 = taylor_d1.reshape(B, inp_length, nregs).sum(axis=1)
            summed_d2 = np.zeros((B, nregs, nregs))

        # 4. Combine linear and quadratic components by regressor
        by_reg = summed_d2.copy()
        for r in range(nregs):
            # The linear (1st order) term only applies to the direct regressor (the diagonal)
            by_reg[:, r, r] += summed_d1[:, r]

        # Total change is the sum of all linear and quadratic terms
        chunk_full_change = summed_d1.sum(axis=1) + summed_d2.sum(axis=(1, 2))

        full_tp_change.append(chunk_full_change)
        by_reg_tp_change.append(by_reg)

    return mdl_out_change, np.concatenate(full_tp_change, axis=0), np.concatenate(by_reg_tp_change, axis=0)


def taylor_predict(mdl: model.ActivityPredictor, regressors: np.ndarray, use_d2: bool, take_every: int,
                   predict_ahead=1) -> Tuple[np.ndarray, np.ndarray]:
    """
    For each time t in regressors, evaluates the model, computes the selected derivatives and
    then attempts to predict the model response at time t+n
    :param mdl: The model to use for predictions
    :param regressors: The 2D regressor matrix, n_timesteps x m_regressors
    :param use_d2: If set to False only the first derivative will be used for the prediction
    :param take_every: Only form predictions every n frames to save time
    :param predict_ahead: The number of frames to predict ahead with the taylor expansion
    :returns:
        [0]: (n_timesteps-input_length-predict_ahead)/n long timeseries of taylor predictions
        [1]: (n_timesteps-input_length-predict_ahead)/n long timeseries of actual network outputs
    """
    return taylor_predict_batched(mdl, regressors, use_d2, take_every, predict_ahead)


def _taylor_predict(reg_fix_point: np.ndarray, reg_test: np.ndarray, ann_fix: float, d1: np.ndarray,
                    d2: np.ndarray) -> float:
    """
    Computes the taylor prediction about a point for another test point nearby
    :param reg_fix_point: The regressor input at the fix point where derivatives have been calculated
    :param reg_test: The regressor input for which to predict the ann response
    :param ann_fix: The output of the ann at reg_fix_point
    :param d1: The set of first order partial derivatives at reg_fix_point
    :param d2: The matrix of second order partial derivatives at reg_fix_point
    """
    diff = (reg_test - reg_fix_point).ravel()
    if d2 is None:
        return ann_fix + np.dot(diff, d1)
    return ann_fix + np.dot(diff, d1) + 0.5 * np.sum(np.dot(diff[:, None], diff[None, :]) * d2)


@njit
def _compute_taylor_d2(reg_diff: np.ndarray, d2: np.ndarray, nregs: int, inp_length: int) -> np.ndarray:
    """
    Computes responses belonging to the second derivative, rearranging by regressor
    instead of by time
    :param reg_diff: The difference in regressors as 2D (1 x (n_regs*n_timepoints)) vector
    :param d2: The hessian
    :param nregs: The number of regressors
    :param inp_length: The timelength of each regressor input
    :return: The second derivative contribution ((n_regs*n_timepoints) x (n_regs*n_timepoints))
    """
    taylor_d2_temp = 0.5 * np.dot(reg_diff, reg_diff.T) * d2  # this matrix is organized by time not by regressor
    taylor_d2 = np.empty_like(taylor_d2_temp, dtype=np.float32)
    for row in range(taylor_d2_temp.shape[0]):
        regnum = row % nregs
        time = row // nregs
        row_ix = regnum * inp_length + time
        for col in range(taylor_d2_temp.shape[1]):
            regnum = col % nregs
            time = col // nregs
            col_ix = regnum * inp_length + time
            taylor_d2[row_ix, col_ix] = taylor_d2_temp[row, col]
    return taylor_d2


@njit
def _compute_by_reg(taylor_d1: np.ndarray, taylor_d2: np.ndarray, nregs: int, inp_length: int) -> np.ndarray:
    """
    Aggregates derivative contributions by regressor
    :param taylor_d1: The first partial derivative contributions (by regressor and time vector)
    :param taylor_d2: The second partial derivative contributions (by regressor and time square matrix)
    :param nregs: The number of regressors
    :param inp_length: The number of timepoints
    :return: Contribution aggregated by regressor as array (1 xnregs x nregs) to account for possible interactions
    """
    by_reg = np.full((1, nregs, nregs), 0.0, dtype=np.float32)
    for r1 in range(nregs):
        for r2 in range(nregs):
            if r1 == r2:
                # these are the non-interacting parts which need to take d1 into account
                by_reg[0, r1, r2] += np.sum(taylor_d1[r1 * inp_length:(r1 + 1) * inp_length])
            by_reg[0, r1, r2] += np.sum(
                taylor_d2[r1 * inp_length:(r1 + 1) * inp_length, r2 * inp_length:(r2 + 1) * inp_length])
    return by_reg


def taylor_decompose(mdl: model.ActivityPredictor, regressors: np.ndarray, take_every: int, predict_ahead: int,
                     use_d2=True) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Uses taylor decomposition to predict changes in network output around chosen point using
    all information as well as only the information corresponding to each regressor and their
    interactions terms
    :param mdl: The model to use for predictions
    :param regressors: The 2D regressor matrix, n_timesteps x m_regressors
    :param take_every: Only form predictions every n frames to save time
    :param predict_ahead: The number of frames to predict ahead with the taylor expansion
    :param use_d2: If set to false only the first derivative will be used in the taylor expansion
    :returns:
        [0]: The true change for each timepoint by going predict_ahead frames into the future
                (n_timesteps-input_length-predict_ahead)/n long vector
        [1]: The predicted change for the whole taylor series
                (n_timesteps-input_length-predict_ahead)/n long vector
        [2]: Array of predicted changes by regressors and their interactions
                (n_timesteps-input_length-predict_ahead)/n x n_regressors x n_regressors
    """
    return taylor_decompose_batched(mdl, regressors, take_every, predict_ahead, use_d2)


def data_mean_prediction(mdl: model.ActivityPredictor, x_bar, j_x_bar, h_x_bar, regressors: np.ndarray, take_every: int,
                         use_probability: bool):
    """
    Computes the prediction of responses based on a fixed Taylor expansion of the network around a specific point
    in our case taken to be the data mean
    :param mdl: The CNN model
    :param x_bar: The data mean (or any arbitrary fix point)
    :param j_x_bar: The jacobian of the model at x_bar
    :param h_x_bar: The hession of the model at x_bar
    :param regressors: The 2D regressor matrix, n_timesteps x m_regressors
    :param take_every: Only compute metrics every n frames to save time
    :param use_probability: If set to true, all outputs will be transformed to probabilities via sigmoid transform
    :return:
        [0]: The prediction of the CNN model
        [1]: The prediction of the 2nd order fixed-point expansion
        [2]: The prediction of a linear fixed-point expansion
    """

    # Extract the scalar baseline output at the data mean
    f_x_bar = float(mdl(x_bar).numpy().ravel()[0])
    inp_length = mdl.input_length

    # 1. Gather all sliding window slices into a single batch up front
    indices = np.arange(inp_length - 1, regressors.shape[0], take_every)
    windows = np.array(
        [regressors[i - inp_length + 1: i + 1, :] for i in indices])  # Shape: (N, inp_length, n_regressors)

    # 2. Perform a single batch inference pass through the model
    if use_probability:
        mdl_out = mdl.get_probability(windows)
    else:
        mdl_out = mdl.get_output(windows)

    # 3. Flatten windows and derivatives to calculate Taylor terms across the batch
    d1 = j_x_bar.numpy().ravel()  # Shape: (D,)
    d2 = np.reshape(h_x_bar.numpy(), (d1.size, d1.size))  # Shape: (D, D)

    # Compute the differences to the data mean for all windows simultaneously
    reg_diff_batch = (windows - x_bar).reshape(len(indices), -1)  # Shape: (N, D)

    # Linear Term: f(x_bar) + delta_X • d1
    mean_prediction_lin = f_x_bar + np.dot(reg_diff_batch, d1)  # Shape: (N,)

    # Quadratic Term: 0.5 * sum((delta_X @ d2) * delta_X)
    # This matrix multiplication replaces the inner loop calculation flawlessly
    quad_term = 0.5 * np.sum((reg_diff_batch @ d2) * reg_diff_batch, axis=1)
    mean_prediction = mean_prediction_lin + quad_term  # Shape: (N,)

    if use_probability:
        mean_prediction = utilities.sigmoid(mean_prediction)
        mean_prediction_lin = utilities.sigmoid(mean_prediction_lin)

    return mdl_out, mean_prediction, mean_prediction_lin


def complexity_scores(mdl: model.ActivityPredictor, x_bar, j_x_bar, h_x_bar, regressors: np.ndarray, take_every: int,
                      use_probability: bool):
    """
    Computes complexity scores - the squared correlation of a linear and a squared model around the data mean
    :param mdl: The CNN model
    :param x_bar: The data mean (or any arbitrary fix point)
    :param j_x_bar: The jacobian of the model at x_bar
    :param h_x_bar: The hession of the model at x_bar
    :param regressors: The 2D regressor matrix, n_timesteps x m_regressors
    :param take_every: Only compute metrics every n frames to save time
    :param use_probability: If set to true, all outputs will be transformed to probabilities via sigmoid transform
    :return:
        [0]: The R2 (coefficient of determination) of the linear 1st order approximation
        [1]: The R2 of the 2nd order approximation
    """
    true_model, order_2, order_1 = data_mean_prediction(mdl, x_bar, j_x_bar, h_x_bar, regressors, take_every,
                                                        use_probability)
    ss_tot = np.sum((true_model - np.mean(true_model))**2)
    lin_score = 1 - np.sum((true_model - order_1)**2)/ss_tot
    sq_score = 1 - np.sum((true_model - order_2)**2)/ss_tot
    return lin_score, sq_score


if __name__ == "__main__":
    print("Module for ANN Taylor decomposition")
