"""
Script to save simple data descriptors that can be helpful to tune and interpret outcomes reported by neuro-mine
"""

import argparse
from neuro_mine.lib.processing import load_and_pre_process_data
import numpy as np
from os import path
import neuro_mine.lib.file_handling as fh
from typing import List
import pandas as pd
import matplotlib.pyplot as pl
from neuro_mine.lib.utilities import compute_autocorr_time


def plot_auto_corr_times(ac_times_pred: np.ndarray, ac_times_resp: np.ndarray, time_delta: float) -> pl.Figure:
    """
    Plots autocorrelation times for predictors and responses as box-plots
    """
    # functions for y-axis unit conversion
    def frames_to_time(x):
        return x * time_delta

    def times_to_frame(x):
        return x / time_delta

    ac_times_pred = ac_times_pred[np.isfinite(ac_times_pred)]
    ac_times_resp = ac_times_resp[np.isfinite(ac_times_resp)]

    d_min = min([np.min(ac_times_pred), np.min(ac_times_resp)])
    d_max = max([np.max(ac_times_pred), np.max(ac_times_resp)])
    plot_data = [ac_times_pred, ac_times_resp]
    plot_labels = ["Predictors", "Responses"]
    fig, ax = pl.subplots()
    ax.boxplot(plot_data)
    ax.set_xticks([1, 2], plot_labels)
    ax.set_ylabel("Autocorrelation time [Timepoints]")
    if d_min * 10 < d_max:
        # select logarithmic axis scale if range is larger than 10-fold
        ax.set_yscale("log")
    secax = ax.secondary_yaxis("right", functions=(frames_to_time, times_to_frame))
    secax.set_ylabel("Autocorrelation time [s]")
    fig.tight_layout()
    return fig


def plot_pw_corrs(df_corrs: pd.DataFrame) -> pl.Figure:
    """
    Plots pairwise correlations as a heatmap
    """
    fig, ax = pl.subplots()
    try:
        im = ax.matshow(df_corrs, vmin=-1, vmax=1, cmap="managua_r")
    except ValueError:
        # managua is only supported from matplotlib version 3.10 onwards
        im = ax.matshow(df_corrs, vmin=-1, vmax=1, cmap="coolwarm")
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label("Correlation")
    pl.xticks(range(df_corrs.shape[1]), df_corrs.columns, rotation=80)
    pl.yticks(range(df_corrs.shape[1]), df_corrs.columns)
    fig.tight_layout()
    return fig


def process_episodic(p_files: List[str], r_files: List[str], output_dir: str):
    r_out_prefix = path.splitext(path.split(r_files[0])[-1])[0]
    p_out_prefix = path.splitext(path.split(p_files[0])[-1])[0]
    _, i_pred_data, i_resp_data, i_times, pred_names, resp_names = load_and_pre_process_data(p_files, r_files,
                                                                                                      True,
                                                                                                      1)
    # remove time column from predictors if not used
    if not use_time:
        i_pred_data = [ipd[:, 1:] for ipd in i_pred_data]
        pred_names = pred_names[1:]
    n_epochs = len(i_pred_data)
    if len(pred_names) > 1:
        pw_pred_corrs = np.zeros((n_epochs, len(pred_names), len(pred_names)))
    else:
        pw_pred_corrs = None
    ac_times_preds = None
    ac_times_resps = None
    for i, (ipd, ird) in enumerate(zip(i_pred_data, i_resp_data)):
        if pw_pred_corrs is not None:
            pw_pred_corrs[i, :, :] = np.corrcoef(ipd.T)
        df_predictors = pd.DataFrame(ipd, columns=pred_names)
        df_responses = pd.DataFrame(ird, columns=resp_names)
        if ac_times_preds is None:
            ac_times_preds = compute_autocorr_time(df_predictors)
            ac_times_resps = compute_autocorr_time(df_responses)
        else:
            ac_times_preds += compute_autocorr_time(df_predictors)
            ac_times_resps += compute_autocorr_time(df_responses)
    if pw_pred_corrs is not None:
        pw_pred_corrs = np.mean(pw_pred_corrs, axis=0)
        df_pw_pred_corrs = pd.DataFrame(pw_pred_corrs, index=pred_names, columns=pred_names)
        df_pw_pred_corrs.to_csv(path.join(output_dir, p_out_prefix + "_pairwise_predictor_corrs.csv"))
        fig = plot_pw_corrs(df_pw_pred_corrs)
        fig.savefig(path.join(output_dir, p_out_prefix + "_pairwise_predictor_corrs.pdf"))
    ac_times_preds /= n_epochs
    ac_times_resps /= n_epochs
    ac_times_preds.to_csv(path.join(output_dir, p_out_prefix + "_autocorr_predictors.csv"))
    ac_times_resps.to_csv(path.join(output_dir, r_out_prefix + "_autocorr_responses.csv"))
    ip_diff = np.mean(np.diff(i_times[0]))
    fig = plot_auto_corr_times(np.array(ac_times_preds.iloc[0]), np.array(ac_times_resps.iloc[0]), ip_diff)
    fig.savefig(path.join(output_dir, r_out_prefix + "Autocorrelation_times.pdf"))



def process_single(p_file: str, r_file: str, output_dir: str):
    r_out_prefix = path.splitext(path.split(r_file)[-1])[0]
    p_out_prefix = path.splitext(path.split(p_file)[-1])[0]
    _, i_pred_data, i_resp_data, i_times, pred_names, resp_names = load_and_pre_process_data([p_file],
                                                                                                      [r_file],
                                                                                                      False,
                                                                                                      1)
    # remove time column from predictors if not used
    if not use_time:
        i_pred_data = i_pred_data[:, 1:]
        pred_names = pred_names[1:]
    # always remove time column from responses
    i_resp_data = i_resp_data[:, 1:]
    resp_names = resp_names[1:]
    # compute, save, and plot pairwise predictor correlations
    if i_pred_data.shape[1] > 1:
        pw_pred_corrs = np.corrcoef(i_pred_data.T)
        df_pw_pred_corrs = pd.DataFrame(pw_pred_corrs, index=pred_names, columns=pred_names)
        df_pw_pred_corrs.to_csv(path.join(output_dir, p_out_prefix + "_pairwise_predictor_corrs.csv"))
        fig = plot_pw_corrs(df_pw_pred_corrs)
        fig.savefig(path.join(output_dir, p_out_prefix + "_pairwise_predictor_corrs.pdf"))
    else:
        print("Only one predictor present. Won't output pairwise correlations.", flush=True)
    # for each predictor and response compute and save
    df_predictors = pd.DataFrame(i_pred_data, columns=pred_names)
    df_responses = pd.DataFrame(i_resp_data, columns=resp_names)
    ac_times_preds = compute_autocorr_time(df_predictors)
    ac_times_preds.to_csv(path.join(output_dir, p_out_prefix + "_autocorr_predictors.csv"))
    ac_times_resps = compute_autocorr_time(df_responses)
    ac_times_resps.to_csv(path.join(output_dir, r_out_prefix + "_autocorr_responses.csv"))
    # generate boxplot of autocorrelation times in predictors and responses
    ip_diff = np.mean(np.diff(i_times))
    fig = plot_auto_corr_times(np.array(ac_times_preds.iloc[0]), np.array(ac_times_resps.iloc[0]), ip_diff)
    fig.savefig(path.join(output_dir, r_out_prefix + "Autocorrelation_times.pdf"))


if __name__ == '__main__':

    a_parser = argparse.ArgumentParser(prog="Data-diagnostic",
                                       description="Reports key-characteristics of input data to guide decisions about"
                                                   " potential downsampling of data or orthogonalization of predictors.")
    a_parser.add_argument("-p", "--predictors", help="Path to CSV files of predictors or alternatively "
                                                     "directory with predictor files.",
                          type=str, required=True, nargs='+')
    a_parser.add_argument("-r", "--responses", help="Path to CSV files of responses or alternatively "
                                                    "directory with response files.",
                          type=str, required=True, nargs='+')
    a_parser.add_argument("-ut", "--use_time", help="If set time will be used as one predictor.",
                          action='store_true')
    a_parser.add_argument("-eps", "--episodic", help="If set data is assumed to be episodic with one "
                                                     "predictor and one response file per episode.",
                          action="store_true")
    a_parser.add_argument("-o", "--out_dir", help="Path of the output data folder.",
                          type=str, required=True)

    args = a_parser.parse_args()

    is_episodic = args.episodic
    use_time = args.use_time

    r_paths = fh.process_file_args(args.responses)
    p_paths = fh.process_file_args(args.predictors)

    out_dir = args.out_dir

    if not path.exists(out_dir) or not path.isdir(out_dir):
        raise IOError("Output directory [-o/--out_dir] does not exist or is not a directory.")

    # the following seems redundant given the re-expansion into lists, however, it ensures consistent use
    # of the pairing logic and underlying file sorting
    file_pairs = fh.pair_files(r_paths, p_paths)

    if len(file_pairs) < 2:
        is_episodic = False

    if is_episodic:
        print("#####", flush=True)
        print("For episodic data, episode averages will be reported for a all metrics")
        print("#####", flush=True)
        process_episodic([pair[1] for pair in file_pairs], [pair[0] for pair in file_pairs], out_dir)
    else:
        for rf, pf in file_pairs:
            process_single(pf, rf, out_dir)
