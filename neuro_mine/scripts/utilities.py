
"""
Module with data preparation classes and functions
"""
from __future__ import annotations

import numpy as np
import tensorflow as tf
import neuro_mine.scripts.model
import h5py
from typing import Union, List, Any, Optional
from numba import njit


def create_overwrite(storage: Union[h5py.File, h5py.Group], name: str, data: Any, overwrite: bool,
                     compress=False) -> None:
    """
    Allows to create a new dataset in an hdf5 file an if desired overvwrite any old data
    :param storage: The hdf5 file or group used to store the information
    :param name: The name of the dataset
    :param data: The data
    :param overwrite: If true any old data with the same name will be deleted and subsequently replaced
    :param compress: If true, data will be stored compressed
    """
    if overwrite and name in storage:
        del storage[name]
    if compress:
        storage.create_dataset(name, data=data, compression="gzip", compression_opts=5)
    else:
        storage.create_dataset(name, data=data)


def modelweights_to_hdf5(storage: Union[h5py.File, h5py.Group], m_weights: List[np.ndarray]) -> None:
    """
    Stores tensorflow weights of a model sequentially to an hdf5 file or group to allow for more compact storage
    across many models (NOTE: No states are saved)
    :param storage: The hdf5 file or group used to store the information
    :param m_weights: List of weight arrays returned by keras.model.get_weights()
    """
    storage.create_dataset("n_layers", data=len(m_weights))
    for i, mw in enumerate(m_weights):
        if type(mw) == np.ndarray:
            storage.create_dataset(f"layer_{i}", data=mw, compression="gzip", compression_opts=5)
        else:
            storage.create_dataset(f"layer_{i}", data=mw)


def modelweights_from_hdf5(storage: Union[h5py.File, h5py.Group]) -> List[np.ndarray]:
    """
    Loads tensorflow model weights from an hdf5 file or group
    :param storage: The hdf5 file or group from which to load the information
    :return: List of weight arrays that can be used with keras.model.set_weights() to set model weights
    """
    n_layers = storage["n_layers"][()]
    m_weights = []
    for i in range(n_layers):
        m_weights.append(storage[f"layer_{i}"][()])
    return m_weights


def bootstrap_fractional_r2loss(real: np.ndarray, predicted: np.ndarray, remainder: np.ndarray,
                                n_boot: int) -> np.ndarray:
    """
    Returns bootstrap samples for the loss in r^2 after components are removed from a prediction
    :param real: The real timeseries data
    :param predicted: The full prediction for the timeseries
    :param remainder: The prediction for the timeseries after components have been excluded
    :param n_boot:
    :return: n_boot long vector of fractional loss scores (fraction of r2 that is lost going from full to remainder)
    """
    if real.size != predicted.size or predicted.size != remainder.size:
        raise ValueError("All timeseries inputs must have same length")
    if n_boot <= 1:
        raise ValueError("n_boot must be > 1")
    output = np.empty(n_boot)
    indices = np.arange(real.size)
    # bootstrap loop
    for i in range(n_boot):
        choose = np.random.choice(indices, indices.size, replace=True)
        full_r2 = np.corrcoef(real[choose], predicted[choose])[0, 1]**2
        rem_r2 = np.corrcoef(real[choose], remainder[choose])[0, 1]**2
        output[i] = 1 - rem_r2 / full_r2
    return output


def bootstrap_binned_average(x: np.ndarray, weights: np.ndarray, bins: np.ndarray, n_boot: int) -> np.ndarray:
    """
    Returns bootstrap samples for a weighted histogram (i.e. average of a quantity based on bins of another quantity)
    :param x: The quantity to bin by
    :param weights: The quantity to average
    :param bins: Array of bin boundaries
    :param n_boot: The number of bootstrap samples to generate
    :return: n_boot x (bins.size-1) matrix of binned average bootstrap samples
    """
    if x.ndim > 1 or weights.ndim > 1:
        raise ValueError("Only 1D vectors are supported for x and weights")
    if x.size != weights.size:
        raise ValueError("Each x sample must have an associated weight")
    output = np.empty((n_boot, bins.size - 1))
    indices = np.arange(x.size)
    for i in range(n_boot):
        choose = np.random.choice(indices, indices.size, replace=True)
        x_bs = x[choose]
        w_bs = weights[choose]
        weighted_count = np.histogram(x_bs, bins, weights=w_bs)[0].astype(float)
        count = np.histogram(x_bs, bins)[0].astype(float)
        output[i, :] = weighted_count / count
    return output


def bootstrap(data: np.ndarray, nboot: int, bootfun: callable) -> np.ndarray:
    """
    For a a n_samples x m_features array creates nboot bootstrap variates of bootfun
    :param data: The data to be bootstrapped
    :param nboot: The number of boostrap variates to create
    :param bootfun: The function to apply, must take axis parameter
    :return: nboot x m_features array of bootstrap variates
    """
    indices = np.arange(data.shape[0]).astype(int)
    variates = np.full((nboot, data.shape[1]), np.nan)
    for i in range(nboot):
        chosen = np.random.choice(indices, data.shape[0], True)
        variates[i, :] = bootfun(data[chosen], axis=0)
    return variates


def safe_standardize(x: np.ndarray, axis: Optional[int] = None, epsilon=1e-9) -> np.ndarray:
    """
    Standardizes an array to 0 mean and unit standard deviation avoiding division by 0
    :param x: The array to standardize
    :param axis: The axis along which standardization should be performmed
    :param epsilon: Small constant to add to standard deviation to avoid divide by 0 if sd(x)=0
    :return: The standardized array of same dimension as x
    """
    if x.ndim == 1 or axis is None:
        y = x - np.mean(x)
        y /= (np.std(y) + epsilon)
    else:
        y = x - np.mean(x, axis=axis, keepdims=True)
        y /= (np.std(y, axis=axis, keepdims=True) + epsilon)
    return y


def barcode_cluster(x: np.ndarray, threshold: Union[float, np.ndarray]) -> np.ndarray:
    """
    For n_samples by n_features input matrix assigns a cluster to each member based on "barcoding"
    where all above-threshold features are set to contribute to a sample
    :param x: n_samples x n_features input
    :param threshold: The trehshold(s) above which (all) features contribute - either scalar or n_features vector
    :return: n_samples long vector of cluster numbers. Ordered as if contributions were binary digits with index 0
        of x having highest significance (no contribution would be first, all contributing last)
    """

    def split(m, row_ix=None, index=0):
        if row_ix is None:
            row_ix = np.arange(m.shape[0])
        above = m[m[:, index] > 0]
        rix_above = row_ix[m[:, index] > 0]
        below = m[m[:, index] <= 0]
        rix_below = row_ix[m[:, index] <= 0]
        if above.size == 0 and index == m.shape[1]-1:
            return [rix_below]
        if below.size == 0 and index == m.shape[1]-1:
            return [rix_above]
        if index == m.shape[1]-1:
            return [rix_above, rix_below]
        if above.size == 0:
            return split(below, rix_below, index+1)
        if below.size == 0:
            return split(above, rix_above, index+1)
        return split(above, rix_above, index+1) + split(below, rix_below, index+1)

    if not np.isscalar(threshold):
        if threshold.size != x.shape[1]:
            raise ValueError("Threshold either has to be a scalar or a vector with n_features element")
        threshold = threshold.ravel()[None, :]
    xt = x > threshold
    clustered_indices = split(xt)
    cluster_numbers = np.full(x.shape[0], np.nan)
    for i, clust in enumerate(reversed(clustered_indices)):
        cluster_numbers[clust] = i
    return cluster_numbers


def create_coordinate_grid_points(x: np.ndarray, y: np.ndarray, z: Optional[np.ndarray]) -> np.ndarray:
    """
    Creates linearized grid of all coordinate pairs
    :param x: Vector of x coordinates in the grid
    :param y: Vector of y coordinates in the grid
    :param z: None or vector of z coordinates in the grid
    :return: n x 2 or n x 3 matrix of all points in the grid
    """
    if z is None:
        xv, yv = np.meshgrid(x, y)
        xv = xv.reshape((np.prod(xv.shape),))
        yv = yv.reshape((np.prod(yv.shape),))
        return np.hstack((xv[:, None], yv[:, None]))
    else:
        xv, yv, zv = np.meshgrid(x, y, z)
        xv = xv.reshape((np.prod(xv.shape),))
        yv = yv.reshape((np.prod(yv.shape),))
        zv = zv.reshape((np.prod(zv.shape),))
        return np.hstack((xv[:, None], yv[:, None], zv[:, None]))


@njit
def rearrange_hessian(hessian: np.ndarray, npreds: int, inp_length: int) -> np.ndarray:
    """
    Re-arranges contents of our hessian matrices so that consecutive rows/columns are grouped by predictor
    instead of by time
    :param hessian: The hessian
    :param npreds: The number of predictors
    :param inp_length: The timelength of each regressor input
    :return: The re-arranged hessian
    """
    hessian_r = np.empty_like(hessian, dtype=np.float32)
    for row in range(hessian.shape[0]):
        regnum = row % npreds
        time = row // npreds
        row_ix = regnum * inp_length + time
        for col in range(hessian.shape[1]):
            regnum = col % npreds
            time = col // npreds
            col_ix = regnum * inp_length + time
            hessian_r[row_ix, col_ix] = hessian[row, col]
    return hessian_r


def simulate_response(act_predictor, predictors: np.ndarray) -> np.ndarray:
    """
    Simulate the predicted response of a neuron to an arbitrary input
    :param act_predictor: The model used to predict the response
    :param predictors: n_time x m_predictors matrix of predictor inputs
    :return: n_time - history_length + 1 long vector of predicted neural responses
    """
    history = act_predictor.input_length
    pred = [act_predictor.get_output(predictors[None, t - history + 1:t + 1, :]) for t in
            range(history - 1, predictors.shape[0])]
    return np.hstack(pred)


def modified_gram_schmidt(col_mat: np.ndarray) -> np.ndarray:
    """
    Performs orthogonalization of col_mat such that in case of linear dependence, linearly
    dependent columns will be set to all 0
    :param col_mat: mxn matrix with columns containing features
    :return: mxn matrix with orthogonalized columns
    """
    # initialize with copy
    v = col_mat.copy()
    # iterate through all columns
    for j in range(v.shape[1]):
        # if the current column is linearly dependent to previous columns
        # its values will be close to 0 - we set to 0 exactly and move on
        if np.allclose(v[:, j], 0):
            v[:, j] = np.zeros(v.shape[0])
            continue
        n = np.linalg.norm(v[:, j])
        q = v[:, j] / n  # this is the unit vector we will  project out all *subsequent* columns one-by-one
        for k in range(j+1, v.shape[1]):
            v[:, k] = v[:, k] - (q@v[:, k])*q
    # set vector lengths to unit norm (in a safe manner avoiding div-0 for 0 vectors)
    norms = np.linalg.norm(v, axis=0, keepdims=True)
    norms[norms < 1e-9] = 1e-9
    v /= norms
    return v


class Data:
    def __init__(self, input_steps, regressors: list, ca_responses: np.ndarray, tsteps_for_train=-1):
        """
        Creates a new Data class
        :param input_steps: The number of regressor timesteps into the past to use to model the response
        :param regressors: List of regressors. Vectors are shared for all ca_responses, while matrices must have
            same shape as ca_responses
        :param ca_responses: n_responses x m_timesteps matrix of cell calcium responses
        :param tsteps_for_train: If negative use all samples for training if positive use first m samples only
        """
        self.data_len = ca_responses.shape[1]
        self.n_responses = ca_responses.shape[0]
        self.regressors = []
        for i, reg in enumerate(regressors):
            if reg.ndim > 2:
                raise ValueError(f"Regressor {i} has more than 2 dimensions")
            elif reg.ndim == 2:
                if reg.shape[0] != 1 and reg.shape[0] != self.n_responses:
                    raise ValueError(f"Regressor {i} is matrix but does not have same amount of samples "
                                     f"as ca_responses")
                if reg.shape[1] != self.data_len:
                    raise ValueError(f"Regressor {i} needs to have same amount of timesteps as ca_responses")
            else:
                if reg.size != self.data_len:
                    raise ValueError(f"Regressor {i} needs to have same amount of timesteps as ca_responses")
                reg = reg[None, :]  # augment shape
            self.regressors.append(reg)
        self.ca_responses = ca_responses
        self.input_steps = input_steps
        if tsteps_for_train > 0:
            self.tsteps_for_train = tsteps_for_train
        elif tsteps_for_train == 0:
            raise ValueError("tsteps_for_train has to be either negative or larger 0")
        else:
            self.tsteps_for_train = ca_responses.shape[1]

    def training_data(self, sample_ix: int, batch_size=32):
        """
        Creates training data for the indicated calcium response sample (cell)
        :param sample_ix: The index of the cell
        :param batch_size: The training batch size to use
        :return: Tensorflow dataset that can be used for training with randomization
        """
        out_data = self.ca_responses[sample_ix, self.input_steps-1:self.tsteps_for_train].copy()
        in_data = np.full((out_data.size, self.input_steps, len(self.regressors)), np.nan).astype(np.float32)
        for i, reg in enumerate(self.regressors):
            if reg.shape[0] == 1:
                this_reg = reg
            else:
                this_reg = reg[sample_ix, :][None, :]
            for t in range(self.input_steps-1, out_data.size+self.input_steps-1):
                in_data[t-self.input_steps+1, :, i] = this_reg[0, t-self.input_steps+1:t+1]
        train_ds = tf.data.Dataset.from_tensor_slices((in_data, out_data)).\
            shuffle(in_data.shape[0], reshuffle_each_iteration=True).batch(batch_size, drop_remainder=True)
        return train_ds.prefetch(tf.data.AUTOTUNE)

    def test_data(self, sample_ix: int, batch_size=32):
        """
        Creates test data for the indicated calcium response sample (cell)
        :param sample_ix: The index of the cell
        :param batch_size: The training batch size to use
        :return: Tensorflow dataset that can be used for testing
        """
        if self.tsteps_for_train == self.ca_responses.shape[1]:
            raise ValueError("All data is training data")
        out_data = self.ca_responses[sample_ix, self.tsteps_for_train+self.input_steps-1:].copy()
        in_data = np.full((out_data.size, self.input_steps, len(self.regressors)), np.nan).astype(np.float32)
        for i, reg in enumerate(self.regressors):
            if reg.shape[0] == 1:
                this_reg = reg
            else:
                this_reg = reg[sample_ix, :][None, :]
            for t in range(self.input_steps-1, out_data.size+self.input_steps-1):
                t_t = t + self.tsteps_for_train
                in_data[t-self.input_steps+1, :, i] = this_reg[0, t_t-self.input_steps+1:t_t+1]
        test_ds = tf.data.Dataset.from_tensor_slices((in_data, out_data)).batch(batch_size, drop_remainder=False)
        return test_ds.prefetch(tf.data.AUTOTUNE)

    def regressor_matrix(self, sample_ix: int) -> np.ndarray:
        """
        For a given sample returns regressor matrix
        :param sample_ix: The index of the cell
        :return: n_timesteps x m_regressors matrix of regressors for the given cell
        """
        reg_data = np.full((self.ca_responses.shape[1], len(self.regressors)), np.nan).astype(np.float32)
        for i, reg in enumerate(self.regressors):
            if reg.shape[0] == 1:
                this_reg = reg
            else:
                this_reg = reg[sample_ix, :]
            reg_data[:, i] = this_reg.ravel().copy()
        return reg_data

    def predict_response(self, sample_ix: int, act_predictor):
        """
        Obtains the predicted response for a given cell
        :param sample_ix: The index of the cell
        :param act_predictor: The model to perform the prediction
        :return:
            [0]: n_timesteps-input_steps+1 sized vector of response prediction
            [1]: Corresponding timesteps in the original calcium response
        """
        if act_predictor.input_length != self.input_steps:
            raise ValueError("Input length of activity prediction model and data class mismatch")
        regressors = self.regressor_matrix(sample_ix)
        pred = simulate_response(act_predictor, regressors)
        return pred, self.ca_responses[sample_ix, self.input_steps-1:]

    def subset(self, sample_indices: List[int]) -> Data:
        """
        Returns a subset of the data, copying  responses and predictors for the indicated cell indices
        :param sample_indices: List of cell indices which should be contained in the new data object
        :return: A data object with only the indicated subset of cells and associated predictors
        """
        new_regs = []
        for r in self.regressors:
            if r.shape[0] == 1:
                new_regs.append(r.copy())
            else:
                new_regs.append(r[sample_indices, :].copy())
        new_ca_responses = self.ca_responses[sample_indices, :].copy()
        return Data(self.input_steps, new_regs, new_ca_responses, self.tsteps_for_train)

    def save(self, filename: str, overwrite=False) -> None:
        """
        Serializes the data instance to an hdf5 file
        :param filename: The path and name of the hdf5 file to save to
        :param overwrite: If set to true and file already exists it will be overwritten if False and exists will fail
        """
        with h5py.File(filename, mode='w' if overwrite else 'x') as dfile:
            self.save_direct(dfile, overwrite)

    def save_direct(self, file: Union[h5py.File, h5py.Group], overwrite=False) -> None:
        """
        Serializes the data instance to an hdf5 file object or group in a file
        :param file: The hdf5 file object
        :param overwrite: If set to true and contents already exists will be overwritten if False and exists will fail
        """
        create_overwrite(file, "input_steps", self.input_steps, overwrite)
        create_overwrite(file, "tsteps_for_train", self.tsteps_for_train, overwrite)
        create_overwrite(file, "ca_responses", self.ca_responses, overwrite)
        create_overwrite(file, "n_regressors", len(self.regressors), overwrite)  # saved  for purposes of easy loading
        if "regressors" not in file:
            r_group = file.create_group("regressors")
        else:
            r_group = file["regressors"]
        for i, r in enumerate(self.regressors):
            create_overwrite(r_group, str(i), r, overwrite)

    @staticmethod
    def load(filename: str) -> Data:
        """
        Loads a stored data instance from an hdf5 file
        :param filename: The path and name of the hdf5 file containing the stored data instance
        :return: A Data object with the contents loaded from file
        """
        with h5py.File(filename, mode='r') as dfile:
            return Data.load_direct(dfile)

    @staticmethod
    def load_direct(file: Union[h5py.File, h5py.Group]) -> Data:
        """
        Loads a stored data instance directly from an hdf5 file object or group
        :param file: The hdf5 file object
        :return: A Data object with the contents loaded from file
        """
        input_steps = file["input_steps"][()]
        tsteps_for_train = file["tsteps_for_train"][()]
        ca_responses = file["ca_responses"][()]
        n_regressors = file["n_regressors"][()]
        r_group = file["regressors"]
        regressors = []
        for i in range(n_regressors):
            regressors.append(r_group[str(i)][()])
        return Data(input_steps, regressors, ca_responses, tsteps_for_train)


if __name__ == "__main__":
    print("Module with data preparation classes and functions")
