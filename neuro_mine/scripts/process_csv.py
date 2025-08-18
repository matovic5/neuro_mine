import pandas as pd
import numpy as np
from mine import Mine
from utilities import safe_standardize
import h5py
import argparse
import os
from os import path
from PyQt5.QtWidgets import QFileDialog, QApplication
import upsetplot as ups
import matplotlib.pyplot as pl


class MineException(Exception):
    def __init__(self, message):
        super().__init__(message)


if __name__ == '__main__':
    app = QApplication([])
    # the following will prevent tensorflow from using the GPU - as the used models have very low complexity
    # they will generally be fit faster on the CPU - furthermore parallelization currently used
    # will not work if tensorflow is run on the GPU!!
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    a_parser = argparse.ArgumentParser(prog="process_csv.py",
                                       description="Uses MINE to fit and interpret CNN models that relate predictors"
                                                   "identified by one CSV file to responses identified by another.")
    a_parser.add_argument("-p", "--predictors", help="Path to CSV file of predictors.", type=str)
    a_parser.add_argument("-r", "--responses", help="Path to CSV file of responses.", type=str)
    a_parser.add_argument("-ut", "--use_time", help="If set time will be used as one predictor.",
                          action='store_true')
    a_parser.add_argument("-sh", "--run_shuffle", help="If set shuffled controls will be run as well.",
                          action='store_true')
    a_parser.add_argument("-ct", "--th_corr", help="The test correlation threshold to "
                                                   "decide that fit was successful.",
                          type=float, default=np.sqrt(0.5))
    a_parser.add_argument("-ts", "--taylor_sig", help="The significance threshold for taylor expansion.",
                          type=float, default=0.05)
    a_parser.add_argument("-tc", "--taylor_cut", help="The variance fraction that has to be lost to"
                                                      "consider component important for fit.",
                          type=float, default=0.1)
    a_parser.add_argument("-la", "--th_lax", help="The threshold of variance explained by the linear"
                                                      "approximation to consider the fit linear.",
                          type=float, default=0.8)
    a_parser.add_argument("-lsq", "--th_sqr", help="The threshold of variance explained by the 2nd order"
                                                  "approximation to consider the fit 2nd order.",
                          type=float, default=0.5)
    a_parser.add_argument("-n", "--model_name", help="Name of model for file saving purposes.", type=str)
    a_parser.add_argument("-mh", "--history", help="The length of model history in time units.",
                          type=float, default=10.0)
    a_parser.add_argument("-tl", "--taylor_look", help="Determines taylor look ahead as multiplier of history",
                          type=float, default=0.5)

    args = a_parser.parse_args()

    resp_path = args.responses
    if resp_path is None:
        resp_path = QFileDialog.getOpenFileName(filter="CSV (*.csv)", caption="Select response file",
                                                options=QFileDialog.DontUseNativeDialog)[0]
        if resp_path == "":
            app.exit(0)
            raise MineException("No response file selected")
    pred_path = args.predictors
    if pred_path is None:
        pred_path = QFileDialog.getOpenFileName(filter="CSV (*.csv)", caption="Select predictor file",
                                                options=QFileDialog.DontUseNativeDialog)[0]
        if pred_path == "":
            app.exit(0)
            raise MineException("No predictor file selected")
    time_as_pred = args.use_time
    run_shuffle = args.run_shuffle
    test_corr_thresh = args.th_corr
    taylor_sig = args.taylor_sig
    taylor_cutoff = args.taylor_cut
    your_model = args.model_name
    lax_thresh = args.th_lax
    sqr_thresh = args.th_sqr
    history_time = args.history
    taylor_look_fraction = args.taylor_look
    if your_model is None:
        # set to default to file name of predictors
        your_model = path.splitext(path.split(resp_path)[-1])[0]

    # TODO: Implement second configuration "interface" allowing user to specify parameters in a config file

    ###
    # Load and process data
    ###
    pred_data = None
    resp_data = None
    resp_header = np.genfromtxt(resp_path, delimiter=",", max_rows=1, dtype=str)

    try:
        resp_header.astype(float)
        resp_data = np.genfromtxt(resp_path, delimiter=",", skip_header=0)
        resp_has_header = False
    except ValueError:
        resp_data = np.genfromtxt(resp_path, delimiter=",", skip_header=1)
        resp_has_header = True

    pred_header = np.genfromtxt(pred_path, delimiter=",", max_rows=1, dtype=str)

    no_pred_header = False

    try:
        pred_header.astype(float)
        no_pred_header = True
    except ValueError:
        pred_data = np.genfromtxt(pred_path, delimiter=",", skip_header=1)

    if no_pred_header:
        # Without the header we will not proceed
        app.exit(0)
        raise MineException("Please add a descriptive header text to your predictor file; make sure that 'time' is the 1st column")

    pred_time = np.nanmax(pred_data, axis=0)[0]
    resp_time = np.nanmax(resp_data, axis=0)[0]

    pred_times = pred_data[:, 0]
    resp_times = resp_data[:, 0]

    max_allowed_time = min([pred_times.max(), resp_times.max()])
    valid_pred = pred_times <= max_allowed_time
    valid_resp = resp_times <= max_allowed_time
    if np.sum(valid_pred) < np.sum(valid_resp):
        ip_time = pred_times[valid_pred]
    else:
        ip_time = resp_times[valid_resp]

    ip_pred_data = np.hstack(
        [np.interp(ip_time, pred_times[valid_pred], pd[valid_pred])[:, None] for pd in pred_data.T])
    ip_resp_data = np.hstack(
        [np.interp(ip_time, resp_times[valid_resp], rd[valid_resp])[:, None] for rd in resp_data.T])

    if time_as_pred == "Y":
        mine_pred = [safe_standardize(ipd) for ipd in ip_pred_data.T]
    else:
        mine_pred = [safe_standardize(ipd) for ipd in ip_pred_data.T[1:]]

    mine_resp = safe_standardize(ip_resp_data[:, 1:]).T

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

    with h5py.File(path.join(path.split(resp_path)[0], f"{your_model}.hdf5"), "w") as weight_file:
        w_grp = weight_file.create_group(f"{your_model}_weights")
        miner = Mine(2.0 / 3, model_history, test_corr_thresh, True, False, taylor_look_ahead, 5)
        miner.verbose = True
        miner.model_weight_store = w_grp
        mdata = miner.analyze_data(mine_pred, mine_resp)

    # rotate mine_resp on user request and re-fit without computing any Taylor just to get test correlations
    if run_shuffle:
        mine_resp_shuff = np.roll(mine_resp, mine_resp.shape[1] // 2, axis=1)
        with h5py.File(path.join(path.split(resp_path)[0], f"{your_model}.hdf5"), "a") as weight_file:
            w_grp = weight_file.create_group(f"{your_model}_weights_shuffled")
            miner = Mine(2 / 3, model_history, test_corr_thresh, False, False, taylor_look_ahead, 5)
            miner.verbose = True
            miner.model_weight_store = w_grp
            mdata_shuff = miner.analyze_data(mine_pred, mine_resp_shuff)

    with h5py.File(path.join(path.split(resp_path)[0], f"{your_model}_analysis.hdf5"), "w") as ana_file:
        ana_grp = ana_file.create_group(f"analysis")
        mdata.save_to_hdf5(ana_grp)
        if mdata_shuff is not None:
            ana_grp = ana_file.create_group(f"analysis_shuffled")
            mdata_shuff.save_to_hdf5(ana_grp)

    ###
    # Output model insights as csv
    ###
    predictor_columns = pred_header if time_as_pred == 'Y' else pred_header[1:]
    interpret_dict = {"Neuron": [], "Fit": []} | {ph: [] for ph in predictor_columns} | {"Linearity": []}
    interpret_name = f"MINE_Insights_{your_model}.csv"
    n_objects = mdata.correlations_test.size
    # for taylor analysis (which predictors are important) compute our significance levels based on a) user input
    # and b) the number of neurons above threshold which gives the multiple-comparison correction - bonferroni
    min_significance = 1 - taylor_sig / np.sum(mdata.correlations_test >= test_corr_thresh)
    normal_quantiles_by_sigma = np.array([0.682689492137, 0.954499736104, 0.997300203937, 0.999936657516,
                                          0.999999426697, 0.999999998027])
    n_sigma = np.where((min_significance - normal_quantiles_by_sigma) < 0)[0][0] + 1

    for j in range(n_objects):
        neuron = j if not resp_has_header else resp_header[
            j + 1]  # because resp_header still contains the first "time" column
        interpret_dict["Neuron"].append(neuron)
        fit = mdata.correlations_test[j] > test_corr_thresh
        interpret_dict["Fit"].append("Y" if fit else "N")
        if not fit:
            for pc in predictor_columns:
                interpret_dict[pc].append("-")
            interpret_dict["Linearity"].append("-")
        else:
            if mdata.model_lin_approx_scores[j] >= lax_thresh:
                interpret_dict["Linearity"].append("linear")
            else:
                if mdata.mean_exp_scores[j] >= sqr_thresh:
                    interpret_dict["Linearity"].append("quadratic")
                else:
                    interpret_dict["Linearity"].append("cubic+")
            for k, pc in enumerate(predictor_columns):
                taylor_mean = mdata.taylor_scores[j][k][0]
                taylor_std = mdata.taylor_scores[j][k][1]
                taylor_is_sig = taylor_mean - n_sigma * taylor_std - taylor_cutoff
                interpret_dict[pc].append("Y" if taylor_is_sig > 0 else "N")
    interpret_df = pd.DataFrame(interpret_dict)
    interpret_df.to_csv(path.join(path.split(resp_path)[0], interpret_name), index=False)

    # TODO: Figure out a good way to save Jacobians (i.e. receptive fields) - note that each neuron will have a
    #  separate receptive field for each predictor. In other words the shape of the Jacobian will be
    #  n_neurons x n_predictors x n_timepoints. Option 1: Save one output CSV file per predictor which contains
    #  the receptive fields of all neurons. Option 2: Dump them all into an hdf 5 file

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
    fig.savefig(path.join(path.split(resp_path)[0], f"{your_model}_BarcodeUpsetPlot.pdf"))

    # finally quit qt app
    app.exit(0)
