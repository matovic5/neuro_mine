from typing import Dict, Tuple, List, Union
import numpy as np
import pandas as pd
from os import path
import os
import h5py
import file_handling as fh
import json
from utilities import safe_standardize, interp_events
from mine import Mine, MineData, MineSpikingData
import upsetplot as ups
import matplotlib.pyplot as pl
from warnings import filterwarnings


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
            [np.interp(ip_time, pred_times[i][valid_pred[i]], pd[valid_pred[i]])[:, None] for pd in predictor_data[i].T])
        if not is_spike_data:
            ip_resp_data = np.hstack(
                [np.interp(ip_time, resp_times[i][valid_resp[i]], rd[valid_resp[i]])[:, None] for rd in response_data[i].T])
        else:
            ip_resp_data = np.hstack(
                [interp_events(ip_time, resp_times[i][valid_resp[i]], rd[valid_resp[i]])[:, None] for rd in response_data[i].T])
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
        [np.interp(ip_time, pred_times[valid_pred], pd[valid_pred])[:, None] for pd in predictor_data.T])
    if not is_spike_data:
        ip_resp_data = np.hstack(
            [np.interp(ip_time, resp_times[valid_resp], rd[valid_resp])[:, None] for rd in response_data.T])
    else:
        ip_resp_data = np.hstack(
            [interp_events(ip_time, resp_times[valid_resp], rd[valid_resp])[:, None] for rd in response_data.T])
    return ip_pred_data, ip_resp_data, ip_time


def generate_insights(mdata: Union[MineData, MineSpikingData], is_spike_data: bool, predictor_names: List[str],
                      response_names: List[str], **kwargs) -> pd.DataFrame:
    """
    Based on mine analysis data produces a dataframe with information about each response
    :param mdata: MINE output data
    :param is_spike_data: If true, responses are assumed to have been spikes
    :param predictor_names: The names of the predictors used
    :param response_names: The names of the responses that were used in fitting
    :param kwargs: Further arguments about thresholds (test_score_thresh, taylor_sig, taylor_cutoff, lax_thresh, sqr_thresh_
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

    model_scores = mdata.roc_auc_test if is_spike_data else mdata.correlations_test
    interpret_dict = {"Response": [], "Fit": []} | {ph: [] for ph in predictor_names} | {"Linearity": []}
    n_objects = model_scores.size
    # for taylor analysis (which predictors are important) compute our significance levels based on a) user input
    # and b) the number of responses above threshold which gives the multiple-comparison correction - bonferroni
    min_significance = 1 - taylor_sig / np.sum(model_scores >= test_score_thresh)
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


def barcode_cluster_plot(insight_df: pd.DataFrame, predictor_names: List[str]) -> Tuple[pl.Figure, pd.DataFrame]:
    # suppress warning about pandas 3.0 compatibility which is violated by upsetplot
    filterwarnings("ignore", category=FutureWarning)
    barcode_labels = [ph for ph in predictor_names] + ["Nonlinear"]
    barcode = np.hstack([(np.array(insight_df[ph]) == "Y")[:, None] for ph in predictor_names])
    barcode = np.c_[barcode, (np.array(insight_df["Linearity"]) != "linear")[:, None]]
    df_barcode = pd.DataFrame(barcode, columns=barcode_labels)
    aggregate = ups.from_indicators(df_barcode)
    fig = pl.figure()
    up_set = ups.UpSet(aggregate, subset_size='count', min_subset_size=1, facecolor="C1", sort_by='cardinality',
                       sort_categories_by=None)
    axes_dict = up_set.plot(fig)
    axes_dict['intersections'].set_yscale('log')
    return fig, df_barcode


def process_file_pair(resp_path: str, pred_path: str, configuration: Dict):
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

    resp_data, resp_has_header, resp_header = fh.CSVParser(resp_path, "R").load_data()
    pred_data, pred_has_header, pred_header = fh.CSVParser(pred_path, "P").load_data()

    # store all output file in a sub-folder of the response file folder
    output_folder = path.join(path.split(resp_path)[0], "output")
    if not path.exists(output_folder):
        os.makedirs(output_folder)

    # We use a very simple heuristic to detect spiking data and we will not allow for mixed data. In other words
    # a response file either contains all continuous data or all spiking data. When in doubt, we will treat as
    # continuous
    if np.all(np.logical_or(resp_data==0, resp_data==1)):
        is_spike_data = True
        print("Responses are assumed to contain spikes")
    else:
        is_spike_data = False
        print("Responses are assumed to be continuous values not spikes")

    ip_pred_data, ip_resp_data, ip_time = joint_interpolation(pred_data, resp_data, pred_data[:, 0],
                                                              resp_data[:, 0], is_spike_data)

    # Save interpolated data with chosen column names if verbose flag is set
    if miner_verbose:
        df_ip_resp_data = pd.DataFrame(ip_resp_data, columns=resp_header)
        df_ip_resp_data.to_csv(path.join(output_folder, f"MINE_{your_model}_interpolated_responses.csv"), index=False)
        df_ip_pred_data = pd.DataFrame(ip_pred_data, columns=pred_header)
        df_ip_pred_data.to_csv(path.join(output_folder, f"MINE_{your_model}_interpolated_predictors.csv"), index=False)

    # perform data-appropriate standardization of predictors and responses
    # save standardizations for storage
    standardized_predictors, m_pred, s_pred = safe_standardize(ip_pred_data, axis=0)
    if not time_as_pred:
        standardized_predictors = standardized_predictors[:, 1:]
        m_pred = m_pred[1:]
        s_pred = s_pred[1:]
    mine_pred = [sipd for sipd in standardized_predictors.T]
    # In the following the first column is removed since it is time
    if not is_spike_data:
        mine_resp, m_resp, s_resp = safe_standardize(ip_resp_data[:, 1:], axis=0)
        mine_resp = mine_resp.T
    else:
        mine_resp = ip_resp_data[:, 1:].T
        # Since this data is not standardized, we set the subtractive component to 0
        # and the divisive component to 1
        m_resp = np.zeros(mine_resp.shape[0])
        s_resp = np.ones(mine_resp.shape[0])

    configuration["run"]["interpolation_time_delta"] = np.mean(np.diff(ip_time))
    configuration["run"]["is_spike_data"] = is_spike_data
    configuration["run"]["n_predictors"] = len(mine_pred)

    # compute our "frame rate", i.e. frames per time-unit on the interpolated scale
    ip_rate = 1 / np.mean(np.diff(ip_time))
    # based on the rate, compute the number of frames within the model history and taylor-look-ahead
    model_history = int(np.round(history_time * ip_rate, 0))
    if model_history < 1:
        model_history = 1

    configuration["run"]["model_history_frames"] = model_history
    # Save configuration to file
    with open(path.join(output_folder, f"MINE_{your_model}_run_config.json"), 'w') as config_file:
        json.dump(configuration, config_file, indent=2)

    taylor_look_ahead = int(np.round(model_history * taylor_look_fraction, 0))
    if taylor_look_ahead < 1:
        taylor_look_ahead = 1
    print(f"Model history is {model_history} frames")
    print(f"Taylor look ahead is {taylor_look_ahead} frames")

    ###
    # Fit model
    ###
    mdata_shuff = None

    weight_file_name = f"MINE_{your_model}_weights.hdf5"
    with h5py.File(path.join(output_folder, weight_file_name), "w") as weight_file:
        w_grp = weight_file.create_group("fit")
        miner = Mine(miner_train_fraction, model_history, test_score_thresh, True, fit_jacobian,
                     taylor_look_ahead, 5, fit_spikes=is_spike_data)
        miner.n_epochs = fit_epochs
        miner.verbose = miner_verbose
        miner.model_weight_store = w_grp
        mdata = miner.analyze_data(mine_pred, mine_resp)
        # save neuron names
        name_grp = weight_file.create_group("response_names")
        for i, r in enumerate(resp_header[1:]):  # first entry is "Time"
            name_grp.create_dataset(f"{i}", data=r.encode('utf-8'))

    # rotate mine_resp on user request and re-fit without computing any Taylor just to get test correlations
    if run_shuffle:
        mine_resp_shuff = np.roll(mine_resp, mine_resp.shape[1] // 2, axis=1)
        with h5py.File(path.join(output_folder, weight_file_name), "a") as weight_file:
            w_grp = weight_file.create_group("fit_shuffled")
            miner = Mine(miner_train_fraction, model_history, test_score_thresh, False, False,
                         taylor_look_ahead, 5, fit_spikes=is_spike_data)
            miner.n_epochs = fit_epochs
            miner.verbose = miner_verbose
            miner.model_weight_store = w_grp
            mdata_shuff = miner.analyze_data(mine_pred, mine_resp_shuff)

    full_ana_file_name = f"MINE_{your_model}_analysis.hdf5"
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

    ###
    # Output model insights as csv
    ###
    predictor_columns = pred_header if time_as_pred else pred_header[1:]
    response_names = resp_header[1:]
    interpret_name = f"MINE_{your_model}_Insights.csv"
    interpret_df = generate_insights(mdata, is_spike_data, predictor_columns, response_names,
                                     test_score_thresh=test_score_thresh,
                                     taylor_sig=taylor_sig,
                                     taylor_cutoff=taylor_cutoff,
                                     lax_thresh=lax_thresh,
                                     sqr_thresh=sqr_thresh)
    interpret_df.to_csv(path.join(output_folder, interpret_name), index=False)

    # save Jacobians: One CSV file for each predictor, containing the Jacobians for each response
    # column headers will be the time delay relative to t=0, since our modeling is set up
    # such that convolutions are restricted to the past (hence model_history)
    def time_from_index(ix: int) -> float:
        ix_corr = ix - model_history + 1  # at model history is timepoint 0
        return (1/ip_rate) * ix_corr

    model_scores = mdata.roc_auc_test if is_spike_data else mdata.correlations_test
    n_objects = model_scores.size
    if fit_jacobian and np.any(model_scores >= test_score_thresh):
        for i, pc in enumerate(predictor_columns):
            jac_dict = {"Response": []} | {f"{time_from_index(t)}": [] for t in range(model_history)}
            jac_file_name = f"MINE_{your_model}_ReceptiveFields_{pc}.csv"
            for j in range(n_objects):
                if np.any(np.isnan(mdata.jacobians[j, :])):
                    continue
                response = resp_header[j + 1]  # because resp_header still contains the first "time" column
                jac_dict["Response"].append(response)
                # index out the predictor related receptive field
                rf = mdata.jacobians[j, i*model_history:(i+1)*model_history]
                for t in range(model_history):
                    jac_dict[f"{time_from_index(t)}"].append(rf[t])
            df_jac = pd.DataFrame(jac_dict)
            df_jac.to_csv(path.join(output_folder, jac_file_name), index=False)

    # if shuffles were calculated plot fraction of above threshold units in data and shuffle
    # versus correlation threshold levels
    if run_shuffle:
        shuffle_scores = mdata_shuff.roc_auc_test if is_spike_data else mdata_shuff.correlations_test
        fig, axes = pl.subplots(nrows=2)
        c_thresholds = np.linspace(0, 1)
        ab_real = np.full_like(c_thresholds, np.nan)
        ab_shuff = np.full_like(c_thresholds, np.nan)
        for i, ct in enumerate(c_thresholds):
            ab_real[i] = np.sum(model_scores > ct) / n_objects
            ab_shuff[i] = np.sum(shuffle_scores > ct) / n_objects
        enrichment = ab_real / ab_shuff
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
        fig.savefig(path.join(output_folder, f"MINE_{your_model}_TestMetrics.pdf"))

    # plot linearity metrics and thresholds
    if np.any(model_scores >= test_score_thresh):
        fig = pl.figure()
        pl.scatter(mdata.model_lin_approx_scores, mdata.model_2nd_approx_scores, s=2)
        pl.plot([lax_thresh, lax_thresh], [-1, 1], 'k--')
        pl.plot([-1, 1], [sqr_thresh, sqr_thresh], 'k--')
        pl.xlim(-1, 1)
        pl.ylim(-1, 1)
        pl.xlabel("Linear approximation $R^2$")
        pl.ylabel("2nd order approximation $R^2$")
        fig.savefig(path.join(output_folder, f"MINE_{your_model}_LinearityMetrics.pdf"))

        # perform barcode clustering
        fig = barcode_cluster_plot(interpret_df[interpret_df["Fit"] == "Y"], predictor_columns)[0]
        fig.savefig(path.join(output_folder, f"MINE_{your_model}_BarcodeUpsetPlot.pdf"))


if __name__ == '__main__':
    pass
