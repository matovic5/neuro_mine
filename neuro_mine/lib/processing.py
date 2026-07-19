from typing import Dict, Tuple, List, Union, Optional
import numpy as np
import pandas as pd
from os import path
import os
import h5py
from tensorflow.python.ops.metrics_impl import true_positives

from neuro_mine.lib import file_handling as fh
import json
from neuro_mine.lib.utilities import safe_standardize, interp_events, safe_standardize_episodic
from neuro_mine.lib.mine import Mine, MineData, MineSpikingData, MineException, MineWarning, BaseData
from.upsetplot import UpSet, from_indicators
import matplotlib.pyplot as pl
from warnings import warn
import psutil
import datetime


def downsample_data(in_data: np.ndarray, in_time: np.ndarray,
                    factor: int, is_spike_data: bool) -> Tuple[np.ndarray, np.ndarray]:
    """
    Downsamples data by a given factor. Overhangs will be removed
    :param in_data: The data to downsample
    :param in_time: The time of each datapoint before downsampling
    :param factor: The downsampling factor
    :param is_spike_data: If true, data is assumed to be discrete 0/1 spiking data
    :return:
        [0]: The downsampled data
        [1]: The downsampled time
    """
    assert in_data.ndim == 1
    assert in_time.size == in_data.size
    if factor <= 1:
        return in_data, in_time
    # determine the function used for downsampling - in case of continuous data we can take the mean
    # in case of spiking data we have to use max, i.e., if there is at least one spike in the down-sampled
    # bin we call a spike. This does mean that downsampling isn't that ideal for spiking data
    ds_fun = np.max if is_spike_data else np.mean
    # remove overhang
    valid_size = (in_data.size // factor) * factor
    out_time = in_time[:valid_size][::factor]
    out_data = ds_fun(in_data[:valid_size].reshape((in_data.size//factor, factor)), axis=1)
    return out_data, out_time


def downsample_mat_with_time(in_data: np.ndarray, factor: int, is_spike_data: bool) -> np.ndarray:
    assert in_data.ndim == 2
    in_time = in_data[:, 0]
    out_data = []
    out_time = None
    for i in range(1, in_data.shape[1]):
        od, out_time = downsample_data(in_data[:, i], in_time, factor, is_spike_data)
        out_data.append(od[:, None])
    out_data = np.hstack(out_data)
    return np.c_[out_time[:, None], out_data]


def downsample_mat_list(in_list: List[np.ndarray], factor: int, is_spike_data: bool) -> List[np.ndarray]:
    out_list = []
    for item in in_list:
        out_list.append(downsample_mat_with_time(item, factor, is_spike_data))
    return out_list


def ip_time_proposal(pred_times: np.ndarray, resp_times: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    For one set (e.g., episode) of predictor and response data, proposes interpolation times
    :param pred_times:
    :param resp_times:
    :return:
    """
    # define interpolation time as the timespan covered in both datasets at the rate in the file with fewer timepoints
    # within that timespan (i.e. we bin to the lower resolution instead of interpolating to the higher resolution)
    max_allowed_time = min([pred_times.max(), resp_times.max()])
    min_allowed_time = max([pred_times.min(), resp_times.min()])
    valid_pred = np.logical_and(pred_times <= max_allowed_time, pred_times >= min_allowed_time)
    valid_resp = np.logical_and(resp_times <= max_allowed_time, resp_times >= min_allowed_time)
    # define interpolation time based on the less dense data ensuring equal timesteps
    if np.sum(valid_pred) < np.sum(valid_resp):
        ip_time = np.linspace(min_allowed_time, max_allowed_time, np.sum(valid_pred))
    else:
        ip_time = np.linspace(min_allowed_time, max_allowed_time, np.sum(valid_resp))
    return ip_time, valid_pred, valid_resp


def episodic_interpolation(predictor_data: List[np.ndarray], response_data: List[np.ndarray], pred_times: List[np.ndarray],
                        resp_times: List[np.ndarray], is_spike_data: bool) -> Tuple[List[np.ndarray], List[np.ndarray], List[np.ndarray]]:
    """
    Interpolates episodic data to a shared time delta
    :param predictor_data: List of predictor data in each episode
    :param response_data: List of response data in each episode
    :param pred_times: List of predictor times in each episode
    :param resp_times: List of response times in each episode
    :param is_spike_data: Indicates whether responses are continuous (False) or 0/1 events (True)
    :return:
        [0]: List of n_interp_times x n_predictors matrix of interpolated predictors
        [1]: List of n_interp_times x n_responses matrix of interpolated responses
        [2]: List of n_interp_times vector of interpolation times as floats
    """
    if len(predictor_data) != len(response_data) or len(predictor_data) != len(pred_times) or len(predictor_data) != len(resp_times):
        raise ValueError("All input lists must have the same number of elements = episodes")
    n_episodes = len(predictor_data)
    # for each episode build interpolation times with the same time-delta which we set to the minimal
    # time delta proposed across episodes
    min_delta = np.inf  # the chosen delta
    min_times, max_times = [], []  # for each episode the minimum and maximum valid times
    valid_pred, valid_resp = [], []  # for each episode the valid input elements
    for p_times, r_times in zip(pred_times, resp_times):
        tp, vp, vr = ip_time_proposal(p_times, r_times)
        if np.min(np.diff(p_times)) < min_delta:
            min_delta = np.min(np.diff(p_times))
            assert min_delta > 0
        min_times.append(np.min(tp))
        max_times.append(np.max(tp))
        valid_pred.append(vp)
        valid_resp.append(vr)
    # perform interpolation
    ip_preds, ip_resps, ip_times = [], [], []
    for i in range(n_episodes):
        n_frames = int((max_times[i] - min_times[i]) / min_delta)
        ip_time = min_times[i] + np.arange(n_frames) * min_delta
        ip_pred_data = np.hstack(
            [np.interp(ip_time, pred_times[i][valid_pred[i]], pda[valid_pred[i]])[:, None] for pda in predictor_data[i].T])
        if not is_spike_data:
            ip_resp_data = np.hstack(
                [np.interp(ip_time, resp_times[i][valid_resp[i]], rd[valid_resp[i]])[:, None] for rd in response_data[i].T])
        else:
            ip_resp_data = np.hstack(
                [interp_events(ip_time, resp_times[i][valid_resp[i]], rd[valid_resp[i]])[:, None] for rd in response_data[i].T[1:, :]])
            ip_resp_data = np.c_[ip_time[:, None], ip_resp_data]
        ip_preds.append(ip_pred_data)
        ip_resps.append(ip_resp_data)
        ip_times.append(ip_time)
    return ip_preds, ip_resps, ip_times


def joint_interpolation(predictor_data: np.ndarray, response_data: np.ndarray, pred_times: np.ndarray,
                        resp_times: np.ndarray, is_spike_data: bool) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Interpolates predictor and response data such that only overlapping times will be considered and interpolation
    occurs to the lower resolution between predictor and response times.
    :param predictor_data: n_timepoints x n_predictors - can include time column
    :param response_data: n_timepoints x n_responses - can include time column
    :param pred_times: n_timepoints vector of predictor times as floats
    :param resp_times: n_timepoints vector of response times as floats
    :param is_spike_data: Indicates whether responses are continuous (False) or 0/1 events (True)
    :return:
        [0]: n_interp_times x n_predictors matrix of interpolated predictors
        [1]: n_interp_times x n_responses matrix of interpolated responses
        [2]: n_interp_times vector of interpolation times as floats
    """

    ip_time, valid_pred, valid_resp = ip_time_proposal(pred_times, resp_times)

    # perform interpolation
    ip_pred_data = np.hstack(
        [np.interp(ip_time, pred_times[valid_pred], pda[valid_pred])[:, None] for pda in predictor_data.T])
    if not is_spike_data:
        ip_resp_data = np.hstack(
            [np.interp(ip_time, resp_times[valid_resp], rd[valid_resp])[:, None] for rd in response_data.T])
    else:
        ip_resp_data = np.hstack(
            [interp_events(ip_time, resp_times[valid_resp], rd[valid_resp])[:, None] for rd in response_data.T[1:, :]])
        ip_resp_data = np.c_[ip_time[:, None], ip_resp_data]
    return ip_pred_data, ip_resp_data, ip_time


def generate_insights(mdata: Union[MineData, MineSpikingData], predictor_names: List[str],
                      response_names: List[str], **kwargs) -> pd.DataFrame:
    """
    Based on mine analysis data produces a dataframe with information about each response
    :param mdata: MINE output data
    :param predictor_names: The names of the predictors used
    :param response_names: The names of the responses that were used in fitting
    :param kwargs: Further arguments about thresholds (test_score_thresh, taylor_sig, taylor_cutoff, lax_thresh, sqr_thresh_)
    :return: Dataframe with insights about model fits
    """
    if "test_score_thresh" in kwargs:
        test_score_thresh = kwargs["test_score_thresh"]
    else:
        test_score_thresh = np.sqrt(0.5)
    if "taylor_sig" in kwargs:
        taylor_sig = kwargs["taylor_sig"]
    else:
        taylor_sig = 0.05
    if "taylor_cutoff" in kwargs:
        taylor_cutoff = kwargs["taylor_cutoff"]
    else:
        taylor_cutoff = 0.1
    if "lax_thresh" in kwargs:
        lax_thresh = kwargs["lax_thresh"]
    else:
        lax_thresh = 0.8
    if "sqr_thresh" in kwargs:
        sqr_thresh = kwargs["sqr_thresh"]
    else:
        sqr_thresh = 0.5

    # use data object type to infer response type
    is_spike_data = type(mdata) == MineSpikingData

    model_scores = mdata.roc_auc_test if is_spike_data else mdata.correlations_test
    interpret_dict = {"Response": [], "Fit": []} | {ph: [] for ph in predictor_names} | {"Linearity": []}
    n_objects = model_scores.size
    # for taylor analysis (which predictors are important) compute our significance levels based on a) user input
    # and b) the number of responses above threshold which gives the multiple-comparison correction - bonferroni
    n_fit = np.sum(model_scores >= test_score_thresh)
    if n_fit > 1:
        min_significance = 1 - taylor_sig / n_fit
    else:
        min_significance = 1 - taylor_sig
    normal_quantiles_by_sigma = np.array([0.682689492137, 0.954499736104, 0.997300203937, 0.999936657516,
                                          0.999999426697, 0.999999998027])
    n_sigma = np.where((min_significance - normal_quantiles_by_sigma) < 0)[0][0] + 1

    for j in range(n_objects):
        response = response_names[j]
        interpret_dict["Response"].append(response)
        fit = model_scores[j] > test_score_thresh
        interpret_dict["Fit"].append("Y" if fit else "N")
        if not fit:
            for pc in predictor_names:
                interpret_dict[pc].append("-")
            interpret_dict["Linearity"].append("-")
        else:
            if mdata.model_lin_approx_scores[j] >= lax_thresh:
                interpret_dict["Linearity"].append("linear")
            else:
                if mdata.model_2nd_approx_scores[j] >= sqr_thresh:
                    interpret_dict["Linearity"].append("quadratic")
                else:
                    interpret_dict["Linearity"].append("cubic+")
            for k, pc in enumerate(predictor_names):
                taylor_mean = mdata.taylor_scores[j][k][0]
                taylor_std = mdata.taylor_scores[j][k][1]
                taylor_is_sig = taylor_mean - n_sigma * taylor_std - taylor_cutoff
                interpret_dict[pc].append("Y" if taylor_is_sig > 0 else "N")
    return pd.DataFrame(interpret_dict)


def generate_insights_from_file(filepath: str, **kwargs) -> pd.DataFrame:
    """
    Loads an analysis file generated during a run and returns an insight dataframe object
    :param filepath: The path to the hdf5 analysis file
    :param kwargs: Further arguments about thresholds (test_score_thresh, taylor_sig, taylor_cutoff, lax_thresh, sqr_thresh_)
    :return: Dataframe with insights about model fits
    """
    with h5py.File(filepath, "r") as f:
        data_object = BaseData.from_hdf5(f["analysis"])
        name_grp = f["data_names"]
        predictor_bytes = name_grp["predictor_names"][()]
        predictor_names = [pb[0].decode("utf-8") for pb in predictor_bytes]
        response_bytes = name_grp["response_names"][()]
        response_names = [rb[0].decode("utf-8") for rb in response_bytes]
    return generate_insights(data_object, predictor_names, response_names, **kwargs)


def barcode_cluster_plot(insight_df: pd.DataFrame, predictor_names: List[str]) -> Tuple[pl.Figure, pd.DataFrame]:
    barcode_labels = [ph for ph in predictor_names] + ["Nonlinear"]
    barcode = np.hstack([(np.array(insight_df[ph]) == "Y")[:, None] for ph in predictor_names])
    barcode = np.c_[barcode, (np.array(insight_df["Linearity"]) != "linear")[:, None]]
    df_barcode = pd.DataFrame(barcode, columns=barcode_labels)
    aggregate = from_indicators(df_barcode)
    fig = pl.figure()
    up_set = UpSet(aggregate, subset_size='count', min_subset_size=1, facecolor="C1", sort_by='cardinality',
                       sort_categories_by=None)
    axes_dict = up_set.plot(fig)
    axes_dict['intersections'].set_yscale('log')
    return fig, df_barcode


def linearity_metrics_plot(mdata: BaseData, linear_threshold: Optional[float],
                           squared_threshold: Optional[float]) -> pl.Figure:
    """
    Produces a scatter plot of R2 values of linear and squared model approximations together with
    :param mdata: The Mine result data from a fit or reinstantiated from an analysis file
    :param linear_threshold: The linear metric threshold
    :param squared_threshold: The squared or 2nd order threshold
    :return: Figure object
    """
    fig = pl.figure()
    pl.scatter(mdata.model_lin_approx_scores, mdata.model_2nd_approx_scores, s=2)
    if linear_threshold is not None:
        pl.plot([linear_threshold, linear_threshold], [-1, 1], 'k--')
    if squared_threshold is not None:
        pl.plot([-1, 1], [squared_threshold, squared_threshold], 'k--')
    pl.xlim(-1, 1)
    pl.ylim(-1, 1)
    pl.xlabel("Linear approximation $R^2$")
    pl.ylabel("2nd order approximation $R^2$")
    return fig


def test_metrics_plot(mdata: Union[MineData, MineSpikingData], mdata_shuff: Union[MineData, MineSpikingData],
                      test_score_thresh: float) -> pl.Figure:
    """
    Plots the comparison of test scores obtained on real data as well as permuted data to allow judging reasonable test
    score threshold for further analysis.
    :param mdata: The Mine result data from a fit or reinstantiated from an analysis file
    :param mdata_shuff: The Mine result data on permutations from a fit or reinstantiated from an analysis file
    :param test_score_thresh: The currently selected test score threshold
    :return: Figure object
    """
    if type(mdata) == MineSpikingData:
        is_spike_data = True
    else:
        is_spike_data = False
    shuffle_scores = mdata_shuff.roc_auc_test if is_spike_data else mdata_shuff.correlations_test
    model_scores = mdata.roc_auc_test if is_spike_data else mdata.correlations_test
    n_objects = model_scores.size

    fig, axes = pl.subplots(nrows=2)
    c_thresholds = np.linspace(0, 1)
    ab_real = np.full_like(c_thresholds, np.nan)
    ab_shuff = np.full_like(c_thresholds, np.nan)
    for i, ct in enumerate(c_thresholds):
        ab_real[i] = np.sum(model_scores > ct) / n_objects
        ab_shuff[i] = np.sum(shuffle_scores > ct) / n_objects
    divisor = ab_shuff.copy()
    divisor[
        divisor < 1 / n_objects] = 1 / n_objects  # if no shuffle objects were identified we cannot assume infinite enrichment
    enrichment = ab_real / divisor
    axes[0].plot(c_thresholds, ab_real, label="Real data")
    axes[0].plot(c_thresholds, ab_shuff, label="Shuffled data")
    axes[0].plot([test_score_thresh, test_score_thresh], [0, 1], 'k--', label="Threshold")
    metric_label = "ROC AUC" if is_spike_data else "Correlation"
    axes[0].set_xlabel(f"Test {metric_label} cutoff")
    axes[0].set_ylabel("Fraction above threshold")
    axes[0].set_ylim(0, 1)
    axes[0].set_xlim(0, 1)
    axes[0].legend()
    axes[1].plot(c_thresholds, enrichment)
    axes[1].plot([test_score_thresh, test_score_thresh], [np.nanmin(enrichment), np.nanmax(enrichment)], 'k--')
    axes[1].set_xlim(0, 1)
    axes[1].set_xlabel(f"Test {metric_label} cutoff")
    axes[1].set_ylabel("Enrichment over shuffle")
    fig.tight_layout()
    return fig


def time_from_index(ix: int, model_history: int, ip_rate: float) -> float:
    """
    Computes for a given index how far back that is from the current time when saving receptive fields (which are
    in the past)
    :param ix: The index for which to compute the time
    :param model_history: The used model history
    :param ip_rate: The data framerate
    :return: Time representation of index
    """
    ix_corr = ix - model_history + 1  # at model history is timepoint 0
    return (1/ip_rate) * ix_corr


def mem_threshold_warn(ip_pred_data: Union[List[np.ndarray], np.ndarray], model_history: int, is_episodic: bool,
                       threshold_fraction=0.75) -> bool:
    """
    Estimate memory usage of model training and warn user if it exceeds threshold level. Also prints downsampling
    suggestion to reduce memory usage.
    :param ip_pred_data: The prediction data to be used during training
    :param model_history: The number of timepoints in the model history
    :param is_episodic: Indicates whether training is across episodes (i.e., ip_pred_data is a List)
    :param threshold_fraction: The fraction of total memory that can be filled before triggering a warning
    :return: True if memory exceeded threshold level
    """
    # compute expected training data size and warn user if crossing a threshold
    # we set the threshold to 3/4 of the total available memory on the machine
    mem_gb_avail = int(psutil.virtual_memory().total / (1024**3))
    td_gb_thresh = int(mem_gb_avail * threshold_fraction)
    td_byte_thresh = int(td_gb_thresh * 1024**3 / 3)  # division by three to safely account for internal data duplication - a future version ideally avoids this
    td_length = sum([pd.shape[0] for pd in ip_pred_data]) if is_episodic else ip_pred_data.shape[0]
    n_predictors = ip_pred_data[0].shape[1] if is_episodic else ip_pred_data.shape[1]
    td_size = td_length * model_history * n_predictors * 4  # 32-bit float, 4 bytes per number
    if td_size > td_byte_thresh:
        downsample_to_thresh = int(td_size // td_byte_thresh + 2)
        downsample_proposal = 1
        for i in range(2, downsample_to_thresh):
            downsample_proposal += 1
            m_hist = model_history // i
            if m_hist < 1:
                m_hist = 1
            if (td_length//downsample_proposal) * m_hist * n_predictors * 4 < td_byte_thresh:
                break
        print("############################")
        print(f"The total system memory is {mem_gb_avail} GB RAM")
        print(f"Expected training data size is larger than {td_size // (1024**3)} GB.")
        print("This either leads to out-of-memory errors, unexplained crashes or sluggish performance.")
        print("Reducing history length or downsampling data will reduce training data size.")
        print(f"Setting the downsampling factor to {downsample_proposal} will reduce datasize below {td_gb_thresh} GB.")
        print("############################")
        return True
    return False


def process_paired_files(resp_path: List[str], pred_path: List[str], configuration: Dict):
    start_time = datetime.datetime.now()

    your_model = configuration["run"]["model_name"]
    run_shuffle = configuration["config"]["run_shuffle"]
    time_as_pred = configuration["config"]["use_time"]
    history_time = configuration["config"]["history"]
    taylor_look_fraction = configuration["config"]["taylor_look"]
    miner_train_fraction = configuration["config"]["miner_train_fraction"]
    test_score_thresh = configuration["config"]["th_test"]
    fit_jacobian = configuration["config"]["jacobian"]
    fit_epochs = configuration["config"]["n_epochs"]
    miner_verbose = configuration["config"]["miner_verbose"]
    taylor_sig = configuration["config"]["taylor_sig"]
    lax_thresh = configuration["config"]["th_lax"]
    sqr_thresh = configuration["config"]["th_sqr"]
    taylor_cutoff = configuration["config"]["taylor_cut"]
    downsampling = configuration["config"]["downsampling"]
    ignore_mem = configuration["config"]["ignore_memory_warning"]

    if len(resp_path) != len(pred_path):
        raise ValueError("Episodic data needs to have the same number of predictor and response files")

    is_episodic = len(resp_path) > 1

    resp_data = None
    pred_data = None
    resp_data_list = None
    pred_data_list = None
    if is_episodic:
        resp_data_list = []
        pred_data_list = []
        resp_header, pred_header = None, None
        for rp, pp in zip(resp_path, pred_path):
            rda, rhh, rh = fh.CSVParser(rp, "R").load_data()
            if resp_header is None:
                resp_header = rh
            resp_data_list.append(rda)
            pda, phh, ph = fh.CSVParser(pp, "P").load_data()
            if pred_header is None:
                pred_header = ph
            pred_data_list.append(pda)
    else:
        resp_data, resp_has_header, resp_header = fh.CSVParser(resp_path[0], "R").load_data()
        pred_data, pred_has_header, pred_header = fh.CSVParser(pred_path[0], "P").load_data()

    # store all output files in a sub-folder of the response file folder - for episodic data we use the first response
    # file to indicate the storage location, for non-episodic data if response files originate from different locations
    # the output folders will be placed into those locations
    output_folder = path.join(path.split(resp_path[0])[0], f"{your_model}")
    if not path.exists(output_folder):
        os.makedirs(output_folder)
    # the names of the output files are derived from the names of the corresponding response files, or in case of
    # episodic data, from the name of the first response file
    output_file_name = path.splitext(path.split(resp_path[0])[-1])[0]

    # We use a very simple heuristic to detect spiking data and we will not allow for mixed data. In other words
    # a response file either contains all continuous data or all spiking data. When in doubt, we will treat as
    # continuous - the same is true for determination across episodes
    if not is_episodic:
        if np.all(np.logical_or(resp_data[:, 1:]==0, resp_data[:, 1:]==1)):
            is_spike_data = True
            print("Responses are assumed to contain spikes")
        else:
            is_spike_data = False
            print("Responses are assumed to be continuous values not spikes")
    else:
        is_spike_data = True
        for rda in resp_data_list:
            if not np.all(np.logical_or(rda==0, rda==1)):
                is_spike_data = False
        if is_spike_data:
            print("Responses are assumed to contain spikes")
        else:
            print("Responses are assumed to be continuous values not spikes")

    # interpolate and if requested downsample data
    if not is_episodic:
        ip_pred_data, ip_resp_data, ip_time = joint_interpolation(pred_data, resp_data, pred_data[:, 0],
                                                                  resp_data[:, 0], is_spike_data)
        if ip_time.size < 2:
            raise MineException("There are less than two timepoints in the data. No model can be fit.")
        if downsampling > 1:
            ip_pred_data = downsample_mat_with_time(ip_pred_data, downsampling, is_spike_data)
            ip_resp_data = downsample_mat_with_time(ip_resp_data, downsampling, is_spike_data)
            ip_time = ip_pred_data[:, 0]
            if ip_time.size < 2:
                raise MineException("The current downsampling factor reduces the data to less than two timepoints."
                                    " Reduce downsampling")
    else:
        ip_pred_data, ip_resp_data, ip_time = episodic_interpolation(pred_data_list, resp_data_list,
                                                                     [pda[:, 0] for pda in pred_data_list],
                                                                     [rda[:, 0] for rda in resp_data_list], is_spike_data)
        for epix in range(len(ip_time)):
            if ip_time[epix].size < 2:
                raise MineException(f"There are less than two timepoints in episode {epix}")
        if downsampling > 1:
            ip_pred_data = downsample_mat_list(ip_pred_data, downsampling, is_spike_data)
            ip_resp_data = downsample_mat_list(ip_resp_data, downsampling, is_spike_data)
            ip_time = [ipd[:, 0] for ipd in ip_pred_data]
            for epix in range(len(ip_time)):
                if ip_time[epix].size < 2:
                    raise MineException(f"The current downsampling factor reduces the data to less than two timepoints"
                                        f" in episode {epix}. Reduce downsampling")

   # Save interpolated data with chosen column names if verbose flag is set
    if miner_verbose:
        if not is_episodic:
            df_ip_resp_data = pd.DataFrame(ip_resp_data, columns=resp_header)
            df_ip_resp_data.to_csv(path.join(output_folder, f"MINE_{output_file_name}_interpolated_responses.csv"), index=False)
            df_ip_pred_data = pd.DataFrame(ip_pred_data, columns=pred_header)
            df_ip_pred_data.to_csv(path.join(output_folder, f"MINE_{output_file_name}_interpolated_predictors.csv"), index=False)
        else:
            # save one csv file with interpolated data for each episode
            for i, (iprd, ippd) in enumerate(zip(ip_resp_data, ip_pred_data)):
                df_ip_resp_data = pd.DataFrame(iprd, columns=resp_header)
                df_ip_resp_data.to_csv(path.join(output_folder, f"MINE_{output_file_name}_interpolated_responses_ep{i:03d}.csv"),
                                       index=False)
                df_ip_pred_data = pd.DataFrame(ippd, columns=pred_header)
                df_ip_pred_data.to_csv(path.join(output_folder, f"MINE_{output_file_name}_interpolated_predictors_ep{i:03d}.csv"),
                                       index=False)

    # perform data-appropriate standardization of predictors and responses
    # save standardizations for storage
    if not is_episodic:
        standardized_predictors, m_pred, s_pred = safe_standardize(ip_pred_data, axis=0)
        if not time_as_pred:  # remove time column if it is not selected to be included as a predictor
            standardized_predictors = standardized_predictors[:, 1:]
            m_pred = m_pred[:, 1:]
            s_pred = s_pred[:, 1:]
        mine_pred = [sipd for sipd in standardized_predictors.T]
        # For responses the time (first) column is always removed since we do not attempt to predict time
        # Responses do not get standardized if they represent spikes
        if not is_spike_data:
            mine_resp, m_resp, s_resp = safe_standardize(ip_resp_data[:, 1:], axis=0)
            mine_resp = mine_resp.T
        else:
            mine_resp = ip_resp_data[:, 1:].T
            # Since this data is not standardized, we set the subtractive component to 0
            # and the divisive component to 1
            m_resp = np.zeros(mine_resp.shape[0])
            s_resp = np.ones(mine_resp.shape[0])
    else:  # episodic data - we use one standardization across all episodes but take care to keep episodes separate
        standardized_predictors, m_pred, s_pred = safe_standardize_episodic(ip_pred_data, axis=0)
        if not time_as_pred:
            standardized_predictors = [sp[:, 1:] for sp in standardized_predictors]
            m_pred = m_pred[:, 1:]
            s_pred = s_pred[:, 1:]
        mine_pred = [[sipd for sipd in standardized_predictors[i].T] for i in range(len(standardized_predictors))]
        if not is_spike_data:
            mine_resp, m_resp, s_resp = safe_standardize_episodic([ipr[:, 1:] for ipr in ip_resp_data], axis=0)
            mine_resp = [mr.T for mr in mine_resp]
        else:
            mine_resp = [ipr[:, 1:].T for ipr in ip_resp_data]
            m_resp = np.zeros(mine_resp[0].shape[0])
            s_resp = np.ones(mine_resp[0].shape[0])

    if not is_episodic:
        configuration["run"]["interpolation_time_delta"] = np.mean(np.diff(ip_time))
    else:
        configuration["run"]["interpolation_time_delta"] = np.mean(np.diff(ip_time[0]))
    configuration["run"]["is_spike_data"] = is_spike_data
    configuration["run"]["n_predictors"] = len(mine_pred)
    configuration["run"]["is_episodic"] = is_episodic

    # compute our "frame rate", i.e. frames per time-unit on the interpolated scale
    if not is_episodic:
        ip_rate = 1 / np.mean(np.diff(ip_time))
    else:
        ip_rate = 1 / np.mean(np.diff(ip_time[0]))

    # based on the rate, compute the number of frames within the model history and taylor-look-ahead
    model_history = int(np.round(history_time * ip_rate, 0))
    if model_history < 1:
        model_history = 1
    configuration["run"]["model_history_frames"] = model_history
    taylor_look_ahead = int(np.round(model_history * taylor_look_fraction, 0))
    if taylor_look_ahead < 1:
        taylor_look_ahead = 1

    # Set taylor_pred_every based on history length, in other words we will perform taylor prediction starting from
    # frames that are "model_history" apart, since tighter analysis likely won't yield more information due to
    # correlations induced by the model input convolution
    taylor_pred_every = model_history

    # Warn the user if there is a very small amount of training data available
    if not is_episodic:
        if ip_time.size - model_history < 10:
            warn("There are less than 10 datapoints available for training. Training will likely fail.", MineWarning)
    else:
        if sum([ipt.size for ipt in ip_time]) - model_history < 10:
            warn("There are less than 10 datapoints available for training. Training will likely fail.", MineWarning)

    if mem_threshold_warn(ip_pred_data, model_history, is_episodic) and (not ignore_mem):
        print("### EXITING PROGRAM ###")
        print("### Either reduce memory by downsampling or pass -imw flag on command line / set 'ignore memory'"
              " on GUI which will force the run to continue.")
        print("If multiple files were chosen as inputs, processing of other files will continue.")
        return

    # Fit model
    mdata_shuff = None
    weight_file_name = f"MINE_{output_file_name}_weights.hdf5"
    with h5py.File(path.join(output_folder, weight_file_name), "w") as weight_file:
        w_grp = weight_file.create_group("fit")
        miner = Mine(miner_train_fraction, model_history, test_score_thresh, True, fit_jacobian,
                     taylor_look_ahead, taylor_pred_every, fit_spikes=is_spike_data)
        miner.n_epochs = fit_epochs
        miner.verbose = miner_verbose
        miner.model_weight_store = w_grp
        if not is_episodic:
            mdata = miner.analyze_data(mine_pred, mine_resp)
        else:
            mdata = miner.analyze_episodic(mine_pred, mine_resp)
        # save neuron names
        name_grp = weight_file.create_group("response_names")
        for i, r in enumerate(resp_header[1:]):  # first entry is "Time"
            name_grp.create_dataset(f"{i}", data=r.encode('utf-8'))

    # rotate mine_resp on user request and re-fit without computing any Taylor information to get test correlations
    if run_shuffle:
        print("#### RUNNING PERMUTED CONTROL DATA (SHUFFLES) ####", flush=True)
        if not is_episodic:
            mine_resp_shuff = np.roll(mine_resp, mine_resp.shape[1] // 2, axis=1)
        else:
            mine_resp_shuff = [np.roll(mr, mr.shape[1] // 2, axis=1) for mr in mine_resp]
        with h5py.File(path.join(output_folder, weight_file_name), "a") as weight_file:
            w_grp = weight_file.create_group("fit_shuffled")
            miner = Mine(miner_train_fraction, model_history, test_score_thresh, False, False,
                         taylor_look_ahead, taylor_pred_every, fit_spikes=is_spike_data)
            miner.n_epochs = fit_epochs
            miner.verbose = miner_verbose
            miner.model_weight_store = w_grp
            if not is_episodic:
                mdata_shuff = miner.analyze_data(mine_pred, mine_resp_shuff)
            else:
                mdata_shuff = miner.analyze_episodic(mine_pred, mine_resp_shuff)

    # save full analysis results (and results of shuffle if it was requested) to file
    full_ana_file_name = f"MINE_{output_file_name}_analysis.hdf5"
    with h5py.File(path.join(output_folder, full_ana_file_name), "w") as ana_file:
        std_grp = ana_file.create_group("standardization")
        std_grp.create_dataset("m_pred", data=m_pred)
        std_grp.create_dataset("s_pred", data=s_pred)
        std_grp.create_dataset("m_resp", data=m_resp)
        std_grp.create_dataset("s_resp", data=s_resp)
        ana_grp = ana_file.create_group("analysis")
        mdata.save_to_hdf5(ana_grp)
        if mdata_shuff is not None:
            ana_grp = ana_file.create_group("analysis_shuffled")
            mdata_shuff.save_to_hdf5(ana_grp)
        # save names of predictors and responses in analysis file
        name_grp = ana_file.create_group("data_names")
        predictor_columns = pred_header if time_as_pred else pred_header[1:]
        response_names = resp_header[1:]
        name_grp.create_dataset("predictor_names", data=np.vstack([str.encode(pc) for pc in predictor_columns]))
        name_grp.create_dataset("response_names", data=np.vstack([str.encode(rn) for rn in response_names]))

    ###
    # Output model insights as csv
    ###
    interpret_name = f"MINE_{output_file_name}_Insights.csv"
    interpret_df = generate_insights(mdata, predictor_columns, response_names,
                                     test_score_thresh=test_score_thresh,
                                     taylor_sig=taylor_sig,
                                     taylor_cutoff=taylor_cutoff,
                                     lax_thresh=lax_thresh,
                                     sqr_thresh=sqr_thresh)
    model_scores = mdata.roc_auc_test if is_spike_data else mdata.correlations_test
    # perform barcode clustering - store in insight file and as upset-plot
    if np.any(model_scores >= test_score_thresh):
        try:
            fig, df_barcode = barcode_cluster_plot(interpret_df[interpret_df["Fit"] == "Y"], predictor_columns)
            fig.savefig(path.join(output_folder, f"MINE_{output_file_name}_BarcodeUpsetPlot.pdf"))

            # augment insights with barcodes and save
            barcode_cluster_numbers = np.full(interpret_df.shape[0], -1, dtype=int)
            fit_ix = np.arange(interpret_df.shape[0]).astype(int)[interpret_df["Fit"] == "Y"]
            for i, fix in enumerate(fit_ix):
                barcode = np.array(df_barcode.iloc[i]).astype(int)
                barcode_cluster_numbers[fix] = sum([bc*(2**j) for j, bc in enumerate(barcode)])
            interpret_df.insert(interpret_df.shape[1], "Barcode cluster", barcode_cluster_numbers)
        except AttributeError:
            warn("Did not generate barcode upset plot. Not enough fit groups.", MineWarning)
    interpret_df.to_csv(path.join(output_folder, interpret_name), index=False)

    # save Jacobians if requested by user: One CSV file for each predictor, containing the Jacobians for each response
    # column headers will be the time delay relative to t=0, since our modeling is set up
    # such that convolutions are restricted to the past (hence model_history)
    n_objects = model_scores.size
    if fit_jacobian and np.any(model_scores >= test_score_thresh):
        for i, pc in enumerate(predictor_columns):
            jac_dict = {"Response": []} | {f"{time_from_index(t, model_history, ip_rate)}": [] for t in range(model_history)}
            jac_file_name = f"MINE_{output_file_name}_ReceptiveFields_{pc}.csv"
            for j in range(n_objects):
                if np.any(np.isnan(mdata.jacobians[j, :])):
                    continue
                response = resp_header[j + 1]  # because resp_header still contains the first "time" column
                jac_dict["Response"].append(response)
                # index out the predictor related receptive field
                rf = mdata.jacobians[j, i*model_history:(i+1)*model_history]
                for t in range(model_history):
                    jac_dict[f"{time_from_index(t, model_history, ip_rate)}"].append(rf[t])
            df_jac = pd.DataFrame(jac_dict)
            df_jac.to_csv(path.join(output_folder, jac_file_name), index=False)

    # if shuffles were calculated plot fraction of above threshold units in data and shuffle
    # versus correlation threshold levels
    if run_shuffle:
        fig = test_metrics_plot(mdata, mdata_shuff, test_score_thresh)
        fig.savefig(path.join(output_folder, f"MINE_{output_file_name}_TestMetrics.pdf"))

    # plot linearity metrics and thresholds
    if np.any(model_scores >= test_score_thresh):
        fig = linearity_metrics_plot(mdata, lax_thresh, sqr_thresh)
        fig.savefig(path.join(output_folder, f"MINE_{output_file_name}_LinearityMetrics.pdf"))

    # compute elapsed time across all data processing
    end_time = datetime.datetime.now()
    elapsed = end_time - start_time
    # add elapsed time to configuration
    configuration["run"]["time_elapsed_seconds"] = elapsed.total_seconds()
    # Save configuration to file
    with open(path.join(output_folder, f"MINE_{output_file_name}_run_config.json"), 'w') as config_file:
        json.dump(configuration, config_file, indent=2)
    # Print elapsed time to command line
    print(f"#### Analysis completed in {elapsed}. ####", flush=True)


if __name__ == '__main__':
    pass