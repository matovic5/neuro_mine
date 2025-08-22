"""
Module for easy running of MINE on user data
"""
import h5py
import numpy as np
from typing import List, Optional, Union
import neuro_mine.scripts.utilities as utilities
import neuro_mine.scripts.model as model
from neuro_mine.scripts.taylorDecomp import taylor_decompose, d2ca_dr2, complexity_scores
from dataclasses import dataclass
import warnings
from sklearn.metrics import roc_auc_score

@dataclass(frozen=True)
class _BaseData:
    """
    Class for shared MINE return values
    """
    taylor_scores: Optional[np.ndarray]
    taylor_true_change: Optional[np.ndarray]
    taylor_full_prediction: Optional[np.ndarray]
    taylor_by_predictor: Optional[np.ndarray]
    model_lin_approx_scores: Optional[np.ndarray]
    model_2nd_approx_scores: Optional[np.ndarray]
    jacobians: Optional[np.ndarray]
    hessians: Optional[np.ndarray]

    def save_to_hdf5(self, file_object: Union[h5py.File, h5py.Group], overwrite=False) -> None:
        """
        Saves all contents to a hdf5 file or group object
        :param file_object: The file/group to save to
        :param overwrite: If true will overwrite data in the file
        """
        if self.taylor_scores is not None:
            utilities.create_overwrite(file_object, "taylor_scores", self.taylor_scores, overwrite)
            utilities.create_overwrite(file_object, "taylor_true_change", self.taylor_true_change, overwrite)
            utilities.create_overwrite(file_object, "taylor_full_prediction", self.taylor_full_prediction,
                                       overwrite)
            utilities.create_overwrite(file_object, "taylor_by_predictor", self.taylor_by_predictor, overwrite)
        if self.model_lin_approx_scores is not None:
            utilities.create_overwrite(file_object, "model_lin_approx_scores", self.model_lin_approx_scores,
                                       overwrite)
        if self.model_2nd_approx_scores is not None:
            utilities.create_overwrite(file_object, "model_2nd_approx_scores", self.model_2nd_approx_scores,
                                       overwrite)
        if self.jacobians is not None:
            utilities.create_overwrite(file_object, "jacobians", self.jacobians, overwrite)
        if self.hessians is not None:
            utilities.create_overwrite(file_object, "hessians", self.hessians, overwrite)

@dataclass(frozen=True)
class MineData(_BaseData):
    """Class for the return values of MINE"""
    correlations_trained: np.ndarray
    correlations_test: np.ndarray

    def save_to_hdf5(self, file_object: Union[h5py.File, h5py.Group], overwrite=False) -> None:
        """
        Saves all contents to a hdf5 file or group object
        :param file_object: The file/group to save to
        :param overwrite: If true will overwrite data in the file
        """
        super().save_to_hdf5(file_object, overwrite)
        utilities.create_overwrite(file_object, "correlations_trained", self.correlations_trained, overwrite)
        utilities.create_overwrite(file_object, "correlations_test", self.correlations_test, overwrite)


@dataclass(frozen=True)
class MineSpikingData(_BaseData):
    """Class for the return values of MINE after spiking analysis"""
    roc_auc_trained: np.ndarray
    roc_auc_test: np.ndarray

    def save_to_hdf5(self, file_object: Union[h5py.File, h5py.Group], overwrite=False) -> None:
        """
        Saves all contents to a hdf5 file or group object
        :param file_object: The file/group to save to
        :param overwrite: If true will overwrite data in the file
        """
        super().save_to_hdf5(file_object, overwrite)
        utilities.create_overwrite(file_object, "roc_auc_trained", self.roc_auc_trained, overwrite)
        utilities.create_overwrite(file_object, "roc_auc_test", self.roc_auc_test, overwrite)


class MineWarning(Warning):
    def __init__(self, message: str):
        super().__init__(message)


class Mine:
    """
    Class that collects intended model data and provides
    analysis function to be run on user-data
    """
    def __init__(self, train_fraction: float, model_history: int, score_cut: float, compute_taylor: bool,
                 return_jacobians: bool, taylor_look_ahead: int, taylor_pred_every: int, fit_spikes: bool):
        """
        Create a new Mine object
        :param train_fraction: The fraction of frames to use for training 0 < train <= 1
        :param model_history: The number of frames to include in the model "history" (Note 1)
        :param score_cut: Minimum correlation required on test data to compute other metrics
        :param compute_taylor: If true, perform taylor expansion and complexity/nonlin evaluation and return results
        :param return_jacobians: If true, return the model jacobians at the data mean
        :param taylor_look_ahead: How many frames into the future to compute the taylor expansion (usually a few secs)
        :param taylor_pred_every: Every how many frames to compute the taylor expansion to save time
        :param fit_spikes: If true, fit the spiking model
        """
        # Note 1: The ANN model purely looks into the past. However, the convolutional filters
        # can be centered arbitrarily by shifting predictor and response frames relative to
        # each other. See <processMusall.py> for an example
        if train_fraction <= 0 or train_fraction > 1:
            raise ValueError(f"train_fraction must be larger 0 and smaller or equal to 1 not {train_fraction}")
        self.train_fraction = train_fraction
        if model_history < 0:
            raise ValueError("model_history cant be < 0")
        self.model_history = model_history
        self.compute_taylor = compute_taylor
        self.return_jacobians = return_jacobians
        # set following to true to return hessians -
        # Note memory requirements of (n_sample x (n_timepointsxn_predictors)^2) sized array
        self.return_hessians = False
        # set the following to a hdf5 file our group object to store model-weights in subgroups labeled
        # according to "cell_{cell_index}_weights". These model-weights can be loaded into a list compatible
        # with tensorflow.keras.model.set_weights() using the utilities.modelweights_from_hdf5 function
        # NOTE: Before setting the weights, the model has to be initialized to the appropriate model structure
        # by evaluation on an appropriately structured test input
        self.model_weight_store: Union[None, h5py.Group, h5py.File] = None
        self.n_epochs = 100  # sensible default
        self.taylor_look_ahead = taylor_look_ahead
        self.taylor_pred_every = taylor_pred_every
        self.score_cut = score_cut
        self.verbose = True
        self.fit_spikes = fit_spikes

    def analyze_data(self, pred_data: List[np.ndarray], response_data: np.ndarray) -> _BaseData:
        """
        Process given data with MINE
        :param pred_data: Predictor data as a list of n_timepoints long vectors. Predictors are shared among all
            responses
        :param response_data: n_responses x n_timepoints matrix of responses
        :return:
            MineData object with the requested data
        """
        # check for matching sizes
        res_len = response_data.shape[1]
        for i, pd in enumerate(pred_data):
            if pd.size != res_len:
                raise ValueError(f"Predictor {i} has a different number of timesteps than the responses. {pd.size} vs. "
                                 f"{res_len}")
        # warn user if data is not standardized - however for spiking analysis data should not be standardized!
        if not self.fit_spikes:
            if (not np.allclose(np.mean(response_data, 1), 0, atol=1e-2)
                    or not np.allclose(np.std(response_data, 1), 1, atol=1e-2)):
                warnings.warn("WARNING: Response data does not appear standardized to 0 mean and standard deviation 1",
                              MineWarning)
        else:
            if not np.all(np.logical_or(response_data == 0 , response_data == 1)):
                warnings.warn("WARNING: Spike data analysis selected but at least part of the data is neither 1 nor 0",
                              MineWarning)
        # predictors should ideally always be standardized
        for i, pd in enumerate(pred_data):
            if not np.isclose(np.mean(pd), 0, atol=1e-2) or not np.isclose(np.std(pd), 1, atol=1e-2):
                warnings.warn(f"WARNING: Predictor {i} does not appear standardized to 0 mean and standard deviation 1",
                              MineWarning)
        train_frames = int(self.train_fraction * res_len)
        n_predictors = len(pred_data)

        # define our score function
        if self.fit_spikes:
            # the spiking model returns log-probabilities by default, hence need to transform!
            score_function = lambda predicted, real: roc_auc_score(real, utilities.sigmoid(predicted))
        else:
            score_function = lambda predicted, real: np.corrcoef(predicted, real)[0, 1]

        scores_trained = np.full(response_data.shape[0], np.nan)
        scores_test = scores_trained.copy()
        if self.compute_taylor:
            n_taylor = (n_predictors ** 2 - n_predictors) // 2 + n_predictors
            taylor_scores = np.full((response_data.shape[0], n_taylor, 2), np.nan)
            taylor_true_change = []
            taylor_full_prediction = []
            taylor_by_pred = []
            lin_approx_scores = scores_test.copy()
            me_scores = scores_test.copy()
        else:
            taylor_scores = None
            taylor_true_change = None
            taylor_full_prediction = None
            taylor_by_pred = None
            lin_approx_scores = None
            me_scores = None
        if self.return_jacobians:
            all_jacobians = np.full((response_data.shape[0], self.model_history * n_predictors), np.nan)
        else:
            all_jacobians = None
        if self.return_hessians:
            all_hessians = np.full((response_data.shape[0], self.model_history * n_predictors,
                                    self.model_history * n_predictors), np.nan)
        else:
            all_hessians = None

        data_obj = utilities.Data(self.model_history, pred_data, response_data, train_frames)
        # create model once
        m = model.get_standard_model(self.model_history, self.fit_spikes)
        # the following is required to init variables at desired shape
        m(np.random.randn(1, self.model_history, len(data_obj.regressors)).astype(np.float32))
        # save untrained weights to reinitialize model without having to recreate the class which somehow leaks memory
        init_weights = m.get_weights()
        for cell_ix in range(data_obj.ca_responses.shape[0]):
            tset = data_obj.training_data(cell_ix, batch_size=256)
            regressors = data_obj.regressor_matrix(cell_ix)
            # reset weights to pre-trained state
            m.set_weights(init_weights)
            # the following appears to be required to re-init variables?
            m(np.random.randn(1, self.model_history, len(data_obj.regressors)).astype(np.float32))
            # train
            model.train_model(m, tset, self.n_epochs, data_obj.ca_responses.shape[1])
            if self.model_weight_store is not None:
                w_group = self.model_weight_store.create_group(f"cell_{cell_ix}_weights")
                utilities.modelweights_to_hdf5(w_group, m.get_weights())
            # evaluate
            p, r = data_obj.predict_response(cell_ix, m)
            c_tr = score_function(p[:train_frames], r[:train_frames])
            scores_trained[cell_ix] = c_tr
            c_ts = score_function(p[train_frames:], r[train_frames:])
            scores_test[cell_ix] = c_ts
            # if the cell doesn't have a test score of at least score_cut we skip the rest
            # NOTE: This means that some return values will only have one entry for each unit
            # that made the cut - the user will have to handle those cases
            if c_ts < self.score_cut or not np.isfinite(c_ts):
                if self.verbose:
                    print(f"        Unit {cell_ix+1} out of {response_data.shape[0]} fit. "
                          f"Test score={scores_test[cell_ix]} which was below cut-off.")
                continue
            # compute first and second order derivatives
            tset = data_obj.training_data(cell_ix, 256)
            all_inputs = []
            for inp, outp in tset:
                all_inputs.append(inp.numpy())
            x_bar = np.mean(np.vstack(all_inputs), 0, keepdims=True)
            jacobian, hessian = d2ca_dr2(m, x_bar)
            # compute taylor-expansion and nonlinearity evaluation if requested
            if self.compute_taylor:
                # compute taylor expansion
                true_change, pc, by_pred = taylor_decompose(m, regressors, self.taylor_pred_every,
                                                            self.taylor_look_ahead)
                taylor_true_change.append(true_change)
                taylor_full_prediction.append(pc)
                taylor_by_pred.append(by_pred)
                # compute first and 2nd order model predictions
                # for spiking models these need to be computed in probability space not log-probability space
                # since deviations at the extremes in log space do not carry the same wait as deviations close to 0
                lin_score, o2_score = complexity_scores(m, x_bar, jacobian, hessian, regressors, self.taylor_pred_every,
                                                        self.fit_spikes)
                lin_approx_scores[cell_ix] = lin_score
                me_scores[cell_ix] = o2_score
                # compute our by-predictor taylor importance as the fractional loss of r2 when excluding the component
                # for spiking models these need to be computed in probability space not log-probability space
                # since deviations at the extremes in log space do not carry the same wait as deviations close to 0
                if self.fit_spikes:
                    true_change = utilities.sigmoid(true_change)
                    pc = utilities.sigmoid(pc)
                    by_pred = utilities.sigmoid(by_pred)
                off_diag_index = 0
                for row in range(n_predictors):
                    for column in range(n_predictors):
                        if row == column:
                            remainder = pc - by_pred[:, row, column]
                            # Store in the first n_diag indices of taylor_by_pred (i.e. simply at row as indexer)
                            bsample = utilities.bootstrap_fractional_r2loss(true_change, pc, remainder, 1000)
                            taylor_scores[cell_ix, row, 0] = np.mean(bsample)
                            taylor_scores[cell_ix, row, 1] = np.std(bsample)
                        elif row < column:
                            remainder = pc - by_pred[:, row, column] - by_pred[:, column, row]
                            # Store in row-major order in taylor_by_pred after the first n_diag indices
                            bsample = utilities.bootstrap_fractional_r2loss(true_change, pc, remainder, 1000)
                            taylor_scores[cell_ix, n_predictors + off_diag_index, 0] = np.mean(bsample)
                            taylor_scores[cell_ix, n_predictors + off_diag_index, 1] = np.std(bsample)
                            off_diag_index += 1
            if self.return_jacobians or self.return_hessians:
                # compute average predictor
                if self.return_jacobians:
                    jacobian = jacobian.numpy().ravel()
                    # reorder jacobian by n_predictor long chunks of hist_steps timeslices
                    jacobian = np.reshape(jacobian, (self.model_history, n_predictors)).T.ravel()
                    all_jacobians[cell_ix, :] = jacobian
                if self.return_hessians:
                    hessian = np.reshape(hessian.numpy(), (x_bar.shape[2] * self.model_history,
                                                           x_bar.shape[2] * self.model_history))
                    hessian = utilities.rearrange_hessian(hessian, n_predictors, self.model_history)
                    all_hessians[cell_ix, :, :] = hessian
            if self.verbose:
                print(f"        Unit {cell_ix+1} out of {response_data.shape[0]} completed. "
                      f"Test score={scores_test[cell_ix]}")
        if self.compute_taylor:
            # turn the taylor predictions into ndarrays unless no unit passed threshold
            if len(taylor_true_change) > 0:
                if data_obj.ca_responses.shape[0] > 1:
                    taylor_true_change = np.vstack(taylor_true_change)
                    taylor_full_prediction = np.vstack(taylor_full_prediction)
                    taylor_by_pred = np.vstack([pbp[None, :] for pbp in taylor_by_pred])
                else:
                    # only one fit object, just expand dimension to keep things consistent
                    taylor_true_change = taylor_true_change[0][None, :]
                    taylor_full_prediction = taylor_full_prediction[0][None, :]
                    taylor_by_pred = taylor_by_pred[0][None, :]
            else:
                taylor_true_change = np.nan
                taylor_full_prediction = np.nan
                taylor_by_pred = np.nan
        if self.fit_spikes:
            return_data = MineSpikingData(
                roc_auc_test=scores_test,
                roc_auc_trained=scores_trained,
                taylor_scores=taylor_scores,
                taylor_true_change=taylor_true_change,
                taylor_full_prediction=taylor_full_prediction,
                taylor_by_predictor=taylor_by_pred,
                model_lin_approx_scores=lin_approx_scores,
                model_2nd_approx_scores=me_scores,
                jacobians=all_jacobians,
                hessians=all_hessians
            )
        else:
            return_data = MineData(
                correlations_test=scores_test,
                correlations_trained=scores_trained,
                taylor_scores=taylor_scores,
                taylor_true_change=taylor_true_change,
                taylor_full_prediction=taylor_full_prediction,
                taylor_by_predictor=taylor_by_pred,
                model_lin_approx_scores=lin_approx_scores,
                model_2nd_approx_scores=me_scores,
                jacobians=all_jacobians,
                hessians=all_hessians
            )
        return return_data
