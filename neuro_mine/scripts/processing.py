from typing import Dict
import numpy as np
import pandas as pd
from os import path
import os
import h5py
import file_handling as fh
import json
from utilities import safe_standardize, interp_events
from mine import Mine
import upsetplot as ups
import matplotlib.pyplot as pl


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

    pred_times = pred_data[:, 0]
    resp_times = resp_data[:, 0]

    # define interpolation time as the timespan covered in both files at the rate in the file with fewer timepoints
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

    # perform interpolation
    ip_pred_data = np.hstack(
        [np.interp(ip_time, pred_times[valid_pred], pd[valid_pred])[:, None] for pd in pred_data.T])
    if not is_spike_data:
        ip_resp_data = np.hstack(
            [np.interp(ip_time, resp_times[valid_resp], rd[valid_resp])[:, None] for rd in resp_data.T])
    else:
        ip_resp_data = np.hstack(
            [interp_events(ip_time, resp_times[valid_resp], rd[valid_resp])[:, None] for rd in resp_data.T])

    # Save interpolated data with chosen column names
    df_ip_resp_data = pd.DataFrame(ip_resp_data, columns=resp_header)
    df_ip_resp_data.to_csv(path.join(output_folder, f"MINE_{your_model}_interpolated_responses.csv"), index=False)
    df_ip_pred_data = pd.DataFrame(ip_pred_data, columns=pred_header)
    df_ip_pred_data.to_csv(path.join(output_folder, f"MINE_{your_model}_interpolated_predictors.csv"), index=False)

    # perform data-appropriate standardization of predictors and responses
    if time_as_pred == "Y":
        mine_pred = [safe_standardize(ipd) for ipd in ip_pred_data.T]
    else:
        mine_pred = [safe_standardize(ipd) for ipd in ip_pred_data.T[1:]]
    # In the following the first column is removed since it is time
    if not is_spike_data:
        mine_resp = safe_standardize(ip_resp_data[:, 1:]).T
    else:
        mine_resp = ip_resp_data[:, 1:].T

    configuration["run"]["interpolation_time_delta"] = np.mean(np.diff(ip_time))
    configuration["run"]["is_spike_data"] = is_spike_data
    configuration["run"]["n_predictors"] = len(mine_pred)
    with open(path.join(output_folder, f"MINE_{your_model}_run_config.json"), 'w') as config_file:
        json.dump(configuration, config_file, indent=2)

    # compute our "frame rate", i.e. frames per time-unit on the interpolated scale
    ip_rate = 1 / np.mean(np.diff(ip_time))
    # based on the rate, compute the number of frames within the model history and taylor-look-ahead
    model_history = int(np.round(history_time * ip_rate, 0))
    if model_history < 1:
        model_history = 1
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
        ana_grp = ana_file.create_group("analysis")
        mdata.save_to_hdf5(ana_grp)
        if mdata_shuff is not None:
            ana_grp = ana_file.create_group("analysis_shuffled")
            mdata_shuff.save_to_hdf5(ana_grp)

    ###
    # Output model insights as csv
    ###
    model_scores = mdata.roc_auc_test if is_spike_data else mdata.correlations_test
    predictor_columns = pred_header if time_as_pred == 'Y' else pred_header[1:]
    interpret_dict = {"Response": [], "Fit": []} | {ph: [] for ph in predictor_columns} | {"Linearity": []}
    interpret_name = f"MINE_{your_model}_Insights.csv"
    n_objects = model_scores.size
    # for taylor analysis (which predictors are important) compute our significance levels based on a) user input
    # and b) the number of responses above threshold which gives the multiple-comparison correction - bonferroni
    min_significance = 1 - taylor_sig / np.sum(model_scores >= test_score_thresh)
    normal_quantiles_by_sigma = np.array([0.682689492137, 0.954499736104, 0.997300203937, 0.999936657516,
                                          0.999999426697, 0.999999998027])
    n_sigma = np.where((min_significance - normal_quantiles_by_sigma) < 0)[0][0] + 1

    for j in range(n_objects):
        response = resp_header[j + 1]  # because resp_header still contains the first "time" column
        interpret_dict["Response"].append(response)
        fit = model_scores[j] > test_score_thresh
        interpret_dict["Fit"].append("Y" if fit else "N")
        if not fit:
            for pc in predictor_columns:
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
            for k, pc in enumerate(predictor_columns):
                taylor_mean = mdata.taylor_scores[j][k][0]
                taylor_std = mdata.taylor_scores[j][k][1]
                taylor_is_sig = taylor_mean - n_sigma * taylor_std - taylor_cutoff
                interpret_dict[pc].append("Y" if taylor_is_sig > 0 else "N")
    interpret_df = pd.DataFrame(interpret_dict)
    interpret_df.to_csv(path.join(output_folder, interpret_name), index=False)

    # save Jacobians: One CSV file for each predictor, containing the Jacobians for each response
    # column headers will be the time delay relative to t=0, since our modeling is set up
    # such that convolutions are restricted to the past (hence model_history)
    def time_from_index(ix: int) -> float:
        ix_corr = ix - model_history + 1  # at model history is timepoint 0
        return ip_rate * ix_corr

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
        interpret_df = interpret_df[interpret_df["Fit"] == "Y"]
        barcode_labels = [ph for ph in predictor_columns] + ["Nonlinear"]
        barcode = np.hstack([(np.array(interpret_df[ph])=="Y")[:, None] for ph in predictor_columns])
        barcode = np.c_[barcode, (np.array(interpret_df["Linearity"])!="linear")[:, None]]
        df_barcode = pd.DataFrame(barcode, columns=barcode_labels)
        aggregate = ups.from_indicators(df_barcode)
        fig = pl.figure()
        up_set = ups.UpSet(aggregate, subset_size='count', min_subset_size=1, facecolor="C1", sort_by='cardinality',
                           sort_categories_by=None)
        axes_dict = up_set.plot(fig)
        axes_dict['intersections'].set_yscale('log')
        fig.savefig(path.join(output_folder, f"MINE_{your_model}_BarcodeUpsetPlot.pdf"))


if __name__ == '__main__':
    pass
