import argparse

from datetime import datetime

import h5py
import json
import matplotlib.pyplot as pl
from mine import Mine
import numpy as np
import os
from os import path
import pandas as pd
import upsetplot as ups
from utilities import safe_standardize, interp_events
import file_handling as fh

class MineException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ConfigException(Exception):
    def __init__(self, message):
        super().__init__(message)


default_options = {
    "use_time": False,
    "run_shuffle": False,
    "th_test": np.sqrt(0.5),
    "taylor_sig": 0.05,
    "taylor_cut": 0.1,
    "th_lax": 0.8,
    "th_sqr": 0.5,
    "history": 10.0,
    "taylor_look": 0.5,
    "jacobian": False,
    "n_epochs": 100,
    "miner_verbose": False,
    "miner_train_fraction": 2.0/3
}


if __name__ == '__main__':

    # the following will prevent tensorflow from using the GPU - as the used models have very low complexity
    # they will generally be fit faster on the CPU - furthermore parallelization currently used
    # will not work if tensorflow is run on the GPU!!
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    a_parser = argparse.ArgumentParser(prog="process_csv.py",
                                       description="Uses MINE to fit and interpret CNN models that relate predictors"
                                                   "identified by one CSV file to responses identified by another.")
    a_parser.add_argument("-p", "--predictors", help="Path to CSV file of predictors.", type=str, required=True)
    a_parser.add_argument("-r", "--responses", help="Path to CSV file of responses.", type=str, required=True)
    a_parser.add_argument("-ut", "--use_time", help="If set time will be used as one predictor.",
                          action='store_true')
    a_parser.add_argument("-sh", "--run_shuffle", help="If set shuffled controls will be run as well.",
                          action='store_true')
    a_parser.add_argument("-ct", "--th_test", help="The test score threshold to "
                                                   "decide that fit was successful.",
                          type=float, default=default_options['th_test'])
    a_parser.add_argument("-ts", "--taylor_sig", help="The significance threshold for taylor expansion.",
                          type=float, default=default_options['taylor_sig'])
    a_parser.add_argument("-tc", "--taylor_cut", help="The variance fraction that has to be lost to"
                                                      "consider component important for fit.",
                          type=float, default=default_options['taylor_cut'])
    a_parser.add_argument("-la", "--th_lax", help="The threshold of variance explained by the linear"
                                                      "approximation to consider the fit linear.",
                          type=float, default=default_options['th_lax'])
    a_parser.add_argument("-lsq", "--th_sqr", help="The threshold of variance explained by the 2nd order"
                                                  "approximation to consider the fit 2nd order.",
                          type=float, default=default_options['th_sqr'])
    a_parser.add_argument("-n", "--model_name", help="Name of model for file saving purposes.", type=str)
    a_parser.add_argument("-mh", "--history", help="The length of model history in time units.",
                          type=float, default=default_options['history'])
    a_parser.add_argument("-tl", "--taylor_look", help="Determines taylor look ahead as multiplier of history",
                          type=float, default=default_options['taylor_look'])
    a_parser.add_argument("-j", "--jacobian", help="Store the Jacobians (linear receptive fields) for each response.",
                          action='store_true')
    a_parser.add_argument("-o", "--config", help="Path to config file with run parameters.", type=str, default=None)
    a_parser.add_argument("-e", "--n_epochs", help="Number of epochs when fitting model.", type=int,
                          default=default_options['n_epochs'])
    a_parser.add_argument("-mv","--miner_verbose", help="Receive updates on model fitting in command line",
                          action='store_true')
    a_parser.add_argument("-mtf", "--miner_train_fraction", help="The fraction of data to use for training",
                          type=float, default=default_options['miner_train_fraction'])

    args = a_parser.parse_args()

    resp_path = args.responses
    pred_path = args.predictors

    config_dict = None
    if args.config is not None:
        if not path.exists(args.config):
            raise ConfigException("Config file does not exist")
        if not path.isfile(args.config):
            raise ConfigException("Config path is not a file")
        try:
            config_dict = json.load(open(args.config))["config"]
        except json.decoder.JSONDecodeError or UnicodeDecodeError:
            raise ConfigException("Config file does not contain valid JSON")
        except KeyError:
            raise ConfigException("Config file does not contain config section")
    else:
        # set to default options
        config_dict = default_options

    # any argument given on the command line will supersede corresponding options in the config dict
    time_as_pred = config_dict["use_time"] if args.use_time == default_options["use_time"] else args.use_time
    run_shuffle = config_dict["run_shuffle"] if args.run_shuffle == default_options["run_shuffle"] else args.run_shuffle
    test_score_thresh = config_dict["th_test"] if np.isclose(args.th_test, default_options["th_test"]) else args.th_test
    taylor_sig = config_dict["taylor_sig"] if np.isclose(args.taylor_sig, default_options["taylor_sig"]) else args.taylor_sig
    taylor_cutoff = config_dict["taylor_cut"] if np.isclose(args.taylor_cut, default_options["taylor_cut"]) else args.taylor_cut
    lax_thresh = config_dict["th_lax"] if np.isclose(args.th_lax, default_options["th_lax"]) else args.th_lax
    sqr_thresh = config_dict["th_sqr"] if np.isclose(args.th_sqr, default_options["th_sqr"]) else args.th_sqr
    history_time = config_dict["history"] if np.isclose(args.history, default_options["history"]) else args.history
    taylor_look_fraction = config_dict["taylor_look"] if np.isclose(args.taylor_look, default_options["taylor_look"]) else args.taylor_look
    fit_jacobian = config_dict["jacobian"] if args.jacobian == default_options["jacobian"] else args.jacobian
    fit_epochs = config_dict["n_epochs"] if args.n_epochs == default_options["n_epochs"] else args.n_epochs
    miner_train_fraction = config_dict["miner_train_fraction"] if args.miner_train_fraction == default_options["miner_train_fraction"] else args.miner_train_fraction
    miner_verbose = config_dict["miner_verbose"] if args.miner_verbose == default_options["miner_verbose"] else args.miner_verbose

    if args.model_name is None:
        # set to default to file name of predictors
        your_model = datetime.now().strftime("%B_%d_%Y_%I_%M%p")
    else:
        your_model = args.model_name

    # save run information and configuration used as json file which we set up here
    configuration = {
        "config":
            {
                "use_time": time_as_pred,
                "run_shuffle": run_shuffle,
                "th_test": test_score_thresh,
                "taylor_sig": taylor_sig,
                "taylor_cut": taylor_cutoff,
                "th_lax": lax_thresh,
                "th_sqr": sqr_thresh,
                "history": history_time,
                "taylor_look": taylor_look_fraction,
                "jacobian": fit_jacobian,
                "n_epochs": fit_epochs,
                "miner_verbose": miner_verbose,
                "miner_train_fraction": miner_train_fraction
            },
        "run":
            {
                "model_name": your_model,
                "predictor_file": pred_path,
                "response_file": resp_path,
                "timestamp": datetime.now().now().isoformat(),
            }
    }


    ###
    # Load and process data
    ###

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

    pred_time = np.nanmax(pred_data, axis=0)[0]
    resp_time = np.nanmax(resp_data, axis=0)[0]

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

    configuration["run"]["interpolation_time_delta"] = np.mean(np.diff(ip_time))
    with open(path.join(output_folder, f"MINE_{your_model}_run_config.json"), 'w') as config_file:
        json.dump(configuration, config_file, indent=2)

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
    df_ip_pred_data = pd.DataFrame(ip_resp_data, columns=pred_header)
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
        w_grp = weight_file.create_group(f"{your_model}_weights")
        miner = Mine(miner_train_fraction, model_history, test_score_thresh, True, fit_jacobian,
                     taylor_look_ahead, 5, fit_spikes=is_spike_data)
        miner.n_epochs = fit_epochs
        miner.verbose = miner_verbose
        miner.model_weight_store = w_grp
        mdata = miner.analyze_data(mine_pred, mine_resp)

    # rotate mine_resp on user request and re-fit without computing any Taylor just to get test correlations
    if run_shuffle:
        mine_resp_shuff = np.roll(mine_resp, mine_resp.shape[1] // 2, axis=1)
        with h5py.File(path.join(output_folder, weight_file_name), "a") as weight_file:
            w_grp = weight_file.create_group(f"{your_model}_weights_shuffled")
            miner = Mine(miner_train_fraction, model_history, test_score_thresh, False, False,
                         taylor_look_ahead, 5, fit_spikes=is_spike_data)
            miner.n_epochs = fit_epochs
            miner.verbose = miner_verbose
            miner.model_weight_store = w_grp
            mdata_shuff = miner.analyze_data(mine_pred, mine_resp_shuff)

    full_ana_file_name = f"MINE_{your_model}_analysis.hdf5"
    with h5py.File(path.join(output_folder, full_ana_file_name), "w") as ana_file:
        ana_grp = ana_file.create_group(f"analysis")
        mdata.save_to_hdf5(ana_grp)
        if mdata_shuff is not None:
            ana_grp = ana_file.create_group(f"analysis_shuffled")
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

    if fit_jacobian:
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
