"""
Script to predict responses based on previously fit models and new predictor inputs
"""

import argparse
import pandas as pd
import h5py
import os
import file_handling as fh
import json
from os import path
from process_csv import ConfigException
from warnings import warn
import numpy as np
from typing import Optional
from utilities import modelweights_from_hdf5, simulate_response
import model

if __name__ == '__main__':
    # the following will prevent tensorflow from using the GPU - as the used models have very low complexity
    # they will generally be fit faster on the CPU - furthermore parallelization currently used
    # will not work if tensorflow is run on the GPU!!
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    a_parser = argparse.ArgumentParser(prog="response_prediction.py",
                                       description="Uses previously fit models to predict responses based on provided"
                                                   " predictor data.")
    a_parser.add_argument("-p", "--predictors", help="Path to CSV files of predictors or alternatively "
                                                     "directory with predictor files.",
                          type=str, required=True, nargs='+')
    a_parser.add_argument("-o", "--config", help="Path to fit configuration json file.", required=True, type=str)
    a_parser.add_argument("-w", "--weights", help="Path to fit model weights hdf5 file.", required=True, type=str)
    a_parser.add_argument("-a", "--analysis", help="Path to analysis hdf5 file of fit.", required=True, type=str)
    # If a threshold is not provided, predictions for all fit neurons will be performed
    a_parser.add_argument("-ct", "--th_test", help="The test score threshold to decide for which neurons"
                                                   " predictions should be made .",
                          type=float, required=False)

    args = a_parser.parse_args()
    predictor_files = fh.process_file_args(args.predictors)
    run_dict = None
    conf_dict = None
    if not path.exists(args.config):
        raise ConfigException("Config file does not exist")
    if not path.isfile(args.config):
        raise ConfigException("Config path is not a file")
    try:
        run_dict = json.load(open(args.config))["run"]
        conf_dict = json.load(open(args.config))["config"]
    except json.decoder.JSONDecodeError or UnicodeDecodeError:
        raise ConfigException("Config file does not contain valid JSON")
    except KeyError:
        raise ConfigException("Config file does not contain run section")

    n_predictors = run_dict["n_predictors"]
    time_delta = run_dict["interpolation_time_delta"]
    is_spike_data = run_dict["is_spike_data"]
    model_history_frames = run_dict["model_history_frames"]
    use_time = conf_dict["use_time"]

    weight_file = args.weights
    out_dir = path.join(path.split(weight_file)[0], "prediction")
    if not path.exists(out_dir):
        os.makedirs(out_dir)

    above_threshold: Optional[np.ndarray] = None
    with h5py.File(args.analysis, "r") as a_file:
        std_grp = a_file["standardization"]
        m_pred = std_grp["m_pred"][()]
        s_pred = std_grp["s_pred"][()]
        m_resp = std_grp["m_resp"][()]
        s_resp = std_grp["s_resp"][()]
        if args.th_test is not None:
            if is_spike_data:
                above_threshold = a_file['analysis']['roc_auc_test'][()] >= args.th_test
            else:
                above_threshold = a_file['analysis']['correlations_test'][()] >= args.th_test

    # load predictors, interpolate to same time-delta as used for fitting and apply standardization
    # that was applied during fitting
    pred_data = []
    i_times = None
    for pf in predictor_files:
        p_data = fh.CSVParser(pf, "P").load_data()[0]
        pred_times = p_data[:, 0]
        if not use_time:
            p_data = p_data[:, 1:]
        if p_data.shape[1] != n_predictors:
            raise ValueError(f"Prediction file {pf} contains {p_data.shape[1]} predictors but {n_predictors}"
                             f" were used for fitting")
        if not np.isclose(np.mean(np.diff(pred_times)), time_delta):
            warn("Predictor rate differs from training rate. Predictor data will be interpolated.")
        e_length = pred_times[-1] - pred_times[0]
        n_interp = int(e_length / time_delta)
        i_times = np.arange(n_interp)*time_delta + pred_times[0]
        p_data = np.hstack([np.interp(i_times, pred_times, p)[:, None] for p in p_data.T])
        pred_data.append((p_data-m_pred)/s_pred)

    model_inits = np.random.randn(1, model_history_frames, n_predictors).astype(np.float32)

    with h5py.File(weight_file, "r") as w_file:
        fit_group = w_file["fit"]
        n_units = len(fit_group.keys())
        if above_threshold is not None and above_threshold.size != n_units:
            raise ValueError("Mismatch between number of fit networks in weight"
                             " file and test correlations in analysis file.")
        # load response names which are stored as byte-strings - we loop over indices instead of keys
        # to ensure proper ordering
        name_group = w_file["response_names"]
        response_names = []
        for i in range(n_units):
            response_names.append(name_group[f"{i}"][()].decode("utf-8"))
        # For each predictor file in the input, we perform a separate output prediction across all selected units
        for pi, p_data in enumerate(pred_data):
            print("####")
            print(f"Processing predictor file {path.split(predictor_files[pi])[1]}")
            print("####")
            out_name = path.splitext(path.split(predictor_files[pi])[1])[0]
            out_name += "_" + path.splitext(path.split(weight_file)[1])[0]
            out_file_path = path.join(out_dir, out_name+"_prediction.csv")
            prediction_time = i_times[model_history_frames-1:]
            m = model.get_standard_model(model_history_frames, is_spike_data)
            m(model_inits)
            all_predictions = []
            for i in range(n_units):
                if above_threshold is not None and not above_threshold[i]:
                    continue
                w_group = fit_group[f"cell_{i}_weights"]
                model_weights = modelweights_from_hdf5(w_group)
                m.set_weights(model_weights)
                prediction = simulate_response(m, p_data)[:, None]
                assert prediction.size == prediction_time.size
                if is_spike_data:
                    # Transform to probabilities
                    prediction = 1 / (1 + np.exp(-prediction))
                all_predictions.append(prediction)
            all_predictions = np.hstack(all_predictions)
            # undo standardization
            all_predictions *= s_resp
            all_predictions += m_resp
            all_predictions = np.c_[prediction_time[:, None], all_predictions]
            df_predictions = pd.DataFrame(all_predictions, columns=["Time"]+response_names)
            df_predictions.to_csv(out_file_path, index=False)
