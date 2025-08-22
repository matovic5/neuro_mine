"""
Module for decomposing the prediction ANN into piecewise linear functions
via Taylor Series decomposition
"""

import neuro_mine.scripts.model as model
import numpy as np
import tensorflow as tf
from numba import njit
from typing import List, Tuple
from neuro_mine.scripts import utilities


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


def taylor_predict(mdl: model.ActivityPredictor, regressors: np.ndarray, use_d2: bool, take_every: int,
                   predict_ahead=1) -> Tuple[np.ndarray, np.ndarray]:
    """
    For each time t in regressors, evaluates the model, computes the selected derivatives and
    then attempts to predict the model response at time t+1
    :param mdl: The model to use for predictions
    :param regressors: The 2D regressor matrix, n_timesteps x m_regressors
    :param use_d2: If set to False only the first derivative will be used for the prediction
    :param take_every: Only form predictions every n frames to save time
    :param predict_ahead: The number of frames to predict ahead with the taylor expansion
    :returns:
        [0]: (n_timesteps-input_length-predict_ahead)/n long timeseries of taylor predictions
        [1]: (n_timesteps-input_length-predict_ahead)/n long timeseries of actual network outputs
    """
    if predict_ahead < 1:
        raise ValueError("predict_ahead has to be integer >= 1")
    inp_length = mdl.input_length
    mdl_output = []
    taylor_prediction = []
    t = inp_length - 1
    while t < regressors.shape[0]-predict_ahead:
        cur_regs = regressors[None, t - inp_length + 1: t + 1, :]
        next_regs = regressors[None, t - inp_length + 1 + predict_ahead: t + 1 + predict_ahead, :]
        cur_mod_out = mdl.get_output(cur_regs)
        next_mod_out = mdl.get_output(next_regs)
        mdl_output.append(next_mod_out)
        if use_d2:
            d1, d2 = d2ca_dr2(mdl, cur_regs)
            d1 = d1.numpy().ravel()
            d2 = np.reshape(d2.numpy(), (regressors.shape[1] * mdl.input_length,
                                         regressors.shape[1] * mdl.input_length))
        else:
            d1 = dca_dr(mdl, cur_regs)
            d1 = d1.numpy().ravel()
            d2 = None
        tay_pred = _taylor_predict(cur_regs, next_regs, cur_mod_out, d1, d2)
        taylor_prediction.append(tay_pred)
        t += take_every
    return np.hstack(taylor_prediction), np.hstack(mdl_output)


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
    Uses taylor decomposition to predict changes in network output around chosen point using the
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
    if predict_ahead < 1:
        raise ValueError("predict_ahead has to be integer >= 1")
    inp_length = mdl.input_length
    mdl_out_change = []
    full_tp_change = []
    by_reg_tp_change = []
    t = inp_length - 1
    nregs = regressors.shape[1]
    while t < regressors.shape[0]-predict_ahead:
        cur_regs = regressors[None, t - inp_length + 1: t + 1, :]
        next_regs = regressors[None, t - inp_length + 1 + predict_ahead: t + 1 + predict_ahead, :]
        reg_diff = (next_regs - cur_regs).ravel().astype(np.float64)
        cur_mod_out = mdl.get_output(cur_regs)
        next_mod_out = mdl.get_output(next_regs)
        mdl_out_change.append(next_mod_out - cur_mod_out)
        # unfortunately, none of the following are contiguous by regressor but rather by timepoint
        # we therefore need to reshape taylor_d1 and taylor_d2 to allow for easy indexing below
        if use_d2:
            d1, d2 = d2ca_dr2(mdl, cur_regs)
            d1 = d1.numpy().ravel()
            d2 = np.reshape(d2.numpy(), (regressors.shape[1] * mdl.input_length,
                                         regressors.shape[1] * mdl.input_length))
            taylor_d1 = reg_diff * d1.astype(np.float64)
            taylor_d1 = np.reshape(taylor_d1, (inp_length, nregs)).T.ravel()
            taylor_d2 = _compute_taylor_d2(reg_diff[:, None], d2.astype(np.float64), nregs, inp_length)
        else:
            d1 = dca_dr(mdl, cur_regs)
            d1 = d1.numpy().ravel()
            taylor_d1 = reg_diff * d1.astype(np.float64)
            taylor_d1 = np.reshape(taylor_d1, (inp_length, nregs)).T.ravel()
            taylor_d2 = np.zeros((taylor_d1.size, taylor_d1.size))
        full_tp_change.append(np.sum(taylor_d1) + np.sum(taylor_d2))
        by_reg = _compute_by_reg(taylor_d1, taylor_d2, nregs, inp_length)
        by_reg_tp_change.append(by_reg)
        t += take_every
    return np.hstack(mdl_out_change), np.hstack(full_tp_change), np.vstack(by_reg_tp_change)


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
    # NOTE: We should speed this up - create 2nd-order design matrix from input and then directly treat this as a
    # regression problem, replacing the ugly while-loop with a matrix multiplication
    f_x_bar = mdl(x_bar)
    mean_prediction: List[float] = []
    mean_prediction_lin: List[float] = []
    mdl_out: List[float] = []
    inp_length = mdl.input_length
    t: int = inp_length - 1
    # prepare our first and second derivatives at the data mean
    d1 = j_x_bar.numpy().ravel()
    d2 = np.reshape(h_x_bar.numpy(), (regressors.shape[1] * mdl.input_length, regressors.shape[1] * mdl.input_length))
    while t < regressors.shape[0]:
        cur_regs = regressors[None, t - inp_length + 1: t + 1, :]
        # compute our difference to the data mean
        reg_diff = (cur_regs - x_bar).ravel().astype(np.float64)
        # get the actual model prediction at the current point and add to our return
        if use_probability:
            cur_mod_out = mdl.get_probability(cur_regs)
        else:
            cur_mod_out = mdl.get_output(cur_regs)
        mdl_out.append(cur_mod_out)
        # compute taylor decomposition around data mean
        mp_lin = f_x_bar + np.dot(reg_diff, d1)
        mp = mp_lin + 0.5 * np.sum(np.dot(reg_diff[:, None], reg_diff[None, :]) * d2)
        if use_probability:
            mean_prediction.append(utilities.sigmoid(mp))
            mean_prediction_lin.append(utilities.sigmoid(mp_lin))
        else:
            mean_prediction.append(mp)
            mean_prediction_lin.append(mp_lin)
        t += take_every
    return np.hstack(mdl_out), np.hstack(mean_prediction), np.hstack(mean_prediction_lin)


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
