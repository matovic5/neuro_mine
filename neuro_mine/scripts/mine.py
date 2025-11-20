"""
Module for easy running of MINE on user data
"""
import h5py
import numpy as np
from typing import List, Optional, Union
import neuro_mine.scripts.utilities as utilities
import neuro_mine.scripts.model as model
from neuro_mine.scripts.taylorDecomp import taylor_decompose, d2ca_dr2, complexity_scores, data_mean_prediction
from dataclasses import dataclass
import warnings
from sklearn.metrics import roc_auc_score

@dataclass(frozen=True)
class BaseData:
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
class MineData(BaseData):
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
class MineSpikingData(BaseData):
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


class _Outputs:
    """
    Internal class for MINE outputs
    """

    def __init__(self, compute_taylor: bool, return_jacobians: bool, return_hessians: bool, n_responses: int,
                 n_predictors: int, model_history: int):
        """
        Generate a new output collection
        :param compute_taylor: Indicates if Taylor analysis will be performed
        :param return_jacobians: Indicates if Jacobians should be stored
        :param return_hessians: Indicates if hessians should be stored
        :param n_responses: The total number of responses to fit
        :param n_predictors: The total number of predictors to use
        :param model_history: The model historyn length
        """
        # calculate number of taylor components
        n_taylor = (n_predictors ** 2 - n_predictors) // 2 + n_predictors
        self.scores_trained = np.full(n_responses, np.nan)
        self.scores_test = self.scores_trained.copy()
        if compute_taylor:
            self.taylor_scores = np.full((n_responses, n_taylor, 2), np.nan)
            self.taylor_true_change = []
            self.taylor_full_prediction = []
            self.taylor_by_pred = []
            self.lin_approx_scores = self.scores_test.copy()
            self.me_scores = self.scores_test.copy()
        else:
            self.taylor_scores = None
            self.taylor_true_change = None
            self.taylor_full_prediction = None
            self.taylor_by_pred = None
            self.lin_approx_scores = None
            self.me_scores = None
        if return_jacobians:
            self.all_jacobians = np.full((n_responses, model_history * n_predictors), np.nan)
        else:
            self.all_jacobians = None
        if return_hessians:
            self.all_hessians = np.full((n_responses, model_history * n_predictors,
                                         model_history * n_predictors), np.nan)
        else:
            self.all_hessians = None

    def to_mine_data(self, spiking: bool) -> Union[MineSpikingData, MineData]:
        if spiking:
            return MineSpikingData(
                roc_auc_test=self.scores_test,
                roc_auc_trained=self.scores_trained,
                taylor_scores=self.taylor_scores,
                taylor_true_change=self.taylor_true_change,
                taylor_full_prediction=self.taylor_full_prediction,
                taylor_by_predictor=self.taylor_by_pred,
                model_lin_approx_scores=self.lin_approx_scores,
                model_2nd_approx_scores=self.me_scores,
                jacobians=self.all_jacobians,
                hessians=self.all_hessians
            )
        else:
            return MineData(
                correlations_test=self.scores_test,
                correlations_trained=self.scores_trained,
                taylor_scores=self.taylor_scores,
                taylor_true_change=self.taylor_true_change,
                taylor_full_prediction=self.taylor_full_prediction,
                taylor_by_predictor=self.taylor_by_pred,
                model_lin_approx_scores=self.lin_approx_scores,
                model_2nd_approx_scores=self.me_scores,
                jacobians=self.all_jacobians,
                hessians=self.all_hessians
            )


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

    def _check_inputs(self, pred_data: List[np.ndarray], response_data: np.ndarray) -> None:
        """
         Check compatibility and standardization of predictor and response data
        :param pred_data: Predictor data as a list of n_timepoints long vectors. Predictors are shared among all
            responses
        :param response_data: n_responses x n_timepoints matrix of responses
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
            if not np.all(np.logical_or(response_data == 0, response_data == 1)):
                warnings.warn("WARNING: Spike data analysis selected but at least part of the data is neither 1 nor 0",
                              MineWarning)
        # predictors should ideally always be standardized
        for i, pd in enumerate(pred_data):
            if not np.isclose(np.mean(pd), 0, atol=1e-2) or not np.isclose(np.std(pd), 1, atol=1e-2):
                warnings.warn(f"WARNING: Predictor {i} does not appear standardized to 0 mean and standard deviation 1",
                              MineWarning)

    def _create_init_model(self, n_predictors):
        """""
        Generates and initializes model
        """""
        m = model.get_standard_model(self.model_history, self.fit_spikes)
        # the following is required to init variables at desired shape
        m(np.random.randn(1, self.model_history, n_predictors).astype(np.float32))
        # save untrained weights to reinitialize model without having to recreate the class which somehow leaks memory
        init_weights = m.get_weights()
        return m, init_weights

    def analyze_episodic(self, pred_data: List[List[np.ndarray]],
                         response_data: List[np.ndarray]) -> Union[MineSpikingData, MineData]:
        if len(pred_data) != len(response_data):
            raise ValueError(f"Episode count in prediction data {len(pred_data)} does not match response data {len(response_data)}")
        n_predictors = None
        n_responses = None
        for pd, rd in zip(pred_data, response_data):
            if n_predictors is None:
                n_predictors = len(pd)
            else:
                if len(pd) != n_predictors:
                    raise ValueError("Predictor sets across episodes must have the same predictor count")
            if n_responses is None:
                n_responses = rd.shape[0]
            else:
                if rd.shape[0] != n_responses:
                    raise ValueError("Response sets across episodes must have the same response count")
            self._check_inputs(pd, rd)
        train_ep = int(self.train_fraction * len(pred_data))

        # define our score function
        if self.fit_spikes:
            # the spiking model returns log-probabilities by default, hence need to transform!
            score_function = lambda predicted, real: roc_auc_score(real, utilities.sigmoid(predicted))
        else:
            score_function = lambda predicted, real: np.corrcoef(predicted, real)[0, 1]

        # define our outputs
        outs = _Outputs(self.compute_taylor, self.return_jacobians, self.return_hessians, n_responses,
                        n_predictors, self.model_history)

        ep_data = utilities.EpisodicData(self.model_history, pred_data, response_data, train_ep)
        # create model once
        m, init_weights = self._create_init_model(n_predictors)
        for cell_ix in range(n_responses):
            tset = ep_data.training_data(cell_ix, batch_size=256)
            # reset weights to pre-trained state
            m.set_weights(init_weights)
            # the following appears to be required to re-init variables?
            m(np.random.randn(1, self.model_history, n_predictors).astype(np.float32))
            # train
            model.train_model(m, tset, self.n_epochs, 0)
            if self.model_weight_store is not None:
                w_group = self.model_weight_store.create_group(f"cell_{cell_ix}_weights")
                utilities.modelweights_to_hdf5(w_group, m.get_weights())
            # evaluate
            ep_predictions = ep_data.predict_response(cell_ix, m)
            p_train, r_train = [], []
            for epp in ep_predictions[:train_ep]:
                p_train.append(epp[0])
                r_train.append(epp[1])
            p_train = np.hstack(p_train)
            r_train = np.hstack(r_train)
            c_tr = score_function(p_train, r_train)
            outs.scores_trained[cell_ix] = c_tr
            p_test, r_test = [], []
            for epp in ep_predictions[train_ep:]:
                p_test.append(epp[0])
                r_test.append(epp[1])
            c_ts = score_function(p_test, r_test)
            outs.scores_test[cell_ix] = c_ts
            # if the cell doesn't have a test score of at least score_cut we skip the rest
            # NOTE: This means that some return values will only have one entry for each unit
            # that made the cut - the user will have to handle those cases
            if c_ts < self.score_cut or not np.isfinite(c_ts):
                if self.verbose:
                    print(f"        Unit {cell_ix+1} out of {n_responses} fit. "
                          f"Test score={outs.scores_test[cell_ix]} which was below cut-off.")
                continue
            # compute first and second order derivatives
            tset = ep_data.training_data(cell_ix, 256)
            all_inputs = []
            for inp, outp in tset:
                all_inputs.append(inp.numpy())
            x_bar = np.mean(np.vstack(all_inputs), 0, keepdims=True)
            jacobian, hessian = d2ca_dr2(m, x_bar)
            # compute taylor-expansion and nonlinearity evaluation if requested
            if self.compute_taylor:
                regressor_list = ep_data.regressor_matrices(cell_ix)
                # compute taylor expansion - piecewise across episodes
                true_change, pc, by_pred = [], [], []
                for regs in regressor_list:
                    tc, p, bp = taylor_decompose(m, regs, self.taylor_pred_every, self.taylor_look_ahead)
                    true_change.append(tc)
                    pc.append(p)
                    by_pred.append(bp)
                true_change = np.hstack(true_change)
                pc = np.hstack(pc)
                by_pred = np.vstack(by_pred)
                outs.taylor_true_change.append(true_change)
                outs.taylor_full_prediction.append(pc)
                outs.taylor_by_pred.append(by_pred)

                # compute first and 2nd order model predictions - piecewise across episodes then compute scores
                true_model, order_1, order_2 = [], [], []
                for regs in regressor_list:
                    tm, o2, o1 = data_mean_prediction(m, x_bar, jacobian, hessian, regs, self.taylor_pred_every,
                                                      self.fit_spikes)
                    true_model.append(tm)
                    order_1.append(o1)
                    order_2.append(o2)
                true_model = np.hstack(true_model)
                order_1 = np.hstack(order_1)
                order_2 = np.hstack(order_2)
                ss_tot = np.sum((true_model - np.mean(true_model)) ** 2)
                lin_score = 1 - np.sum((true_model - order_1) ** 2) / ss_tot
                o2_score = 1 - np.sum((true_model - order_2) ** 2) / ss_tot
                outs.lin_approx_scores[cell_ix] = lin_score
                outs.me_scores[cell_ix] = o2_score
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
                            outs.taylor_scores[cell_ix, row, 0] = np.mean(bsample)
                            outs.taylor_scores[cell_ix, row, 1] = np.std(bsample)
                        elif row < column:
                            remainder = pc - by_pred[:, row, column] - by_pred[:, column, row]
                            # Store in row-major order in taylor_by_pred after the first n_diag indices
                            bsample = utilities.bootstrap_fractional_r2loss(true_change, pc, remainder, 1000)
                            outs.taylor_scores[cell_ix, n_predictors + off_diag_index, 0] = np.mean(bsample)
                            outs.taylor_scores[cell_ix, n_predictors + off_diag_index, 1] = np.std(bsample)
                            off_diag_index += 1
            if self.return_jacobians or self.return_hessians:
                if self.return_jacobians:
                    jacobian = jacobian.numpy().ravel()
                    # reorder jacobian by n_predictor long chunks of hist_steps timeslices
                    jacobian = np.reshape(jacobian, (self.model_history, n_predictors)).T.ravel()
                    outs.all_jacobians[cell_ix, :] = jacobian
                if self.return_hessians:
                    hessian = np.reshape(hessian.numpy(), (x_bar.shape[2] * self.model_history,
                                                           x_bar.shape[2] * self.model_history))
                    hessian = utilities.rearrange_hessian(hessian, n_predictors, self.model_history)
                    outs.all_hessians[cell_ix, :, :] = hessian
            if self.verbose:
                print(f"        Unit {cell_ix + 1} out of {n_responses} completed. "
                      f"Test score={outs.scores_test[cell_ix]}")
        if self.compute_taylor:
            # turn the taylor predictions into ndarrays unless no unit passed threshold
            if len(outs.taylor_true_change) > 0:
                if len(outs.taylor_true_change) > 1:
                    outs.taylor_true_change = np.vstack(outs.taylor_true_change)
                    outs.taylor_full_prediction = np.vstack(outs.taylor_full_prediction)
                    outs.taylor_by_pred = np.vstack([pbp[None, :] for pbp in outs.taylor_by_pred])
                else:
                    # only one fit object, just expand dimension to keep things consistent
                    outs.taylor_true_change = outs.taylor_true_change[0][None, :]
                    outs.taylor_full_prediction = outs.taylor_full_prediction[0][None, :]
                    outs.taylor_by_pred = outs.taylor_by_pred[0][None, :]
            else:
                outs.taylor_true_change = np.nan
                outs.taylor_full_prediction = np.nan
                outs.taylor_by_pred = np.nan
        return outs.to_mine_data(self.fit_spikes)

    def analyze_data(self, pred_data: List[np.ndarray], response_data: np.ndarray) -> Union[MineSpikingData, MineData]:
        """
        Process given data with MINE
        :param pred_data: Predictor data as a list of n_timepoints long vectors. Predictors are shared among all
            responses
        :param response_data: n_responses x n_timepoints matrix of responses
        :return:
            MineData object with the requested data
        """
        self._check_inputs(pred_data, response_data)
        res_len = response_data.shape[1]
        n_responses = response_data.shape[0]
        train_frames = int(self.train_fraction * res_len)
        n_predictors = len(pred_data)

        # define our score function
        if self.fit_spikes:
            # the spiking model returns log-probabilities by default, hence need to transform!
            score_function = lambda predicted, real: roc_auc_score(real, utilities.sigmoid(predicted))
        else:
            score_function = lambda predicted, real: np.corrcoef(predicted, real)[0, 1]

        # define our outputs
        outs = _Outputs(self.compute_taylor, self.return_jacobians, self.return_hessians, response_data.shape[0],
                        n_predictors, self.model_history)

        data_obj = utilities.Data(self.model_history, pred_data, response_data, train_frames)
        # create model once
        m, init_weights = self._create_init_model(n_predictors)
        for cell_ix in range(n_responses):
            tset = data_obj.training_data(cell_ix, batch_size=256)
            # reset weights to pre-trained state
            m.set_weights(init_weights)
            # the following appears to be required to re-init variables?
            m(np.random.randn(1, self.model_history, n_predictors).astype(np.float32))
            # train
            model.train_model(m, tset, self.n_epochs, 0)
            if self.model_weight_store is not None:
                w_group = self.model_weight_store.create_group(f"cell_{cell_ix}_weights")
                utilities.modelweights_to_hdf5(w_group, m.get_weights())
            # evaluate
            p, r = data_obj.predict_response(cell_ix, m)
            c_tr = score_function(p[:train_frames], r[:train_frames])
            outs.scores_trained[cell_ix] = c_tr
            c_ts = score_function(p[train_frames:], r[train_frames:])
            outs.scores_test[cell_ix] = c_ts
            # if the cell doesn't have a test score of at least score_cut we skip the rest
            # NOTE: This means that some return values will only have one entry for each unit
            # that made the cut - the user will have to handle those cases
            if c_ts < self.score_cut or not np.isfinite(c_ts):
                if self.verbose:
                    print(f"        Unit {cell_ix+1} out of {n_responses} fit. "
                          f"Test score={outs.scores_test[cell_ix]} which was below cut-off.")
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
                regressors = data_obj.regressor_matrix(cell_ix)
                # compute taylor expansion
                true_change, pc, by_pred = taylor_decompose(m, regressors, self.taylor_pred_every,
                                                            self.taylor_look_ahead)
                outs.taylor_true_change.append(true_change)
                outs.taylor_full_prediction.append(pc)
                outs.taylor_by_pred.append(by_pred)
                # compute first and 2nd order model predictions
                # for spiking models these need to be computed in probability space not log-probability space
                # since deviations at the extremes in log space do not carry the same wait as deviations close to 0
                lin_score, o2_score = complexity_scores(m, x_bar, jacobian, hessian, regressors, self.taylor_pred_every,
                                                        self.fit_spikes)
                outs.lin_approx_scores[cell_ix] = lin_score
                outs.me_scores[cell_ix] = o2_score
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
                            outs.taylor_scores[cell_ix, row, 0] = np.mean(bsample)
                            outs.taylor_scores[cell_ix, row, 1] = np.std(bsample)
                        elif row < column:
                            remainder = pc - by_pred[:, row, column] - by_pred[:, column, row]
                            # Store in row-major order in taylor_by_pred after the first n_diag indices
                            bsample = utilities.bootstrap_fractional_r2loss(true_change, pc, remainder, 1000)
                            outs.taylor_scores[cell_ix, n_predictors + off_diag_index, 0] = np.mean(bsample)
                            outs.taylor_scores[cell_ix, n_predictors + off_diag_index, 1] = np.std(bsample)
                            off_diag_index += 1
            if self.return_jacobians or self.return_hessians:
                if self.return_jacobians:
                    jacobian = jacobian.numpy().ravel()
                    # reorder jacobian by n_predictor long chunks of hist_steps timeslices
                    jacobian = np.reshape(jacobian, (self.model_history, n_predictors)).T.ravel()
                    outs.all_jacobians[cell_ix, :] = jacobian
                if self.return_hessians:
                    hessian = np.reshape(hessian.numpy(), (x_bar.shape[2] * self.model_history,
                                                           x_bar.shape[2] * self.model_history))
                    hessian = utilities.rearrange_hessian(hessian, n_predictors, self.model_history)
                    outs.all_hessians[cell_ix, :, :] = hessian
            if self.verbose:
                print(f"        Unit {cell_ix+1} out of {response_data.shape[0]} completed. "
                      f"Test score={outs.scores_test[cell_ix]}")
        if self.compute_taylor:
            # turn the taylor predictions into ndarrays unless no unit passed threshold
            if len(outs.taylor_true_change) > 0:
                if data_obj.ca_responses.shape[0] > 1:
                    outs.taylor_true_change = np.vstack(outs.taylor_true_change)
                    outs.taylor_full_prediction = np.vstack(outs.taylor_full_prediction)
                    outs.taylor_by_pred = np.vstack([pbp[None, :] for pbp in outs.taylor_by_pred])
                else:
                    # only one fit object, just expand dimension to keep things consistent
                    outs.taylor_true_change = outs.taylor_true_change[0][None, :]
                    outs.taylor_full_prediction = outs.taylor_full_prediction[0][None, :]
                    outs.taylor_by_pred = outs.taylor_by_pred[0][None, :]
            else:
                outs.taylor_true_change = np.nan
                outs.taylor_full_prediction = np.nan
                outs.taylor_by_pred = np.nan
        return outs.to_mine_data(self.fit_spikes)
