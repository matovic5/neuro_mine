import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

from neuro_mine.lib.mine import Mine
import argparse
import os
from time import time
import numpy as np
import pandas as pd
from neuro_mine.lib import utilities

if __name__ == '__main__':
    # the following will prevent tensorflow from using the GPU - as the used models have very low complexity
    # they will generally be fit faster on the CPU - furthermore parallelization currently used
    # will not work if tensorflow is run on the GPU!!
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    a_parser = argparse.ArgumentParser(prog="neuromine_timetrial.py",
                                       description="Tests runtime for various fit configurations.")
    a_parser.add_argument("-o", "--outdir", help="Path to output directory for plots and csv files.",
                          type=str, required=True)
    a_parser.add_argument("-np", "--n_predictors", help="Number of predictors used for fits.", type=int,
                          default=5)
    a_parser.add_argument("-dl", "--data_lengths", help="Data lengths to test for timing.", type=int,
                          nargs='+', required=True)
    a_parser.add_argument("-hl", "--hist_lengths", help="History lengths to test for timing.", type=int,
                          nargs='+', required=True)
    a_parser.add_argument("-e", "--n_epochs", help="Number of epochs when fitting model.", type=int,
                          default=100)

    args = a_parser.parse_args()
    out_dir = args.outdir
    if not os.path.exists(out_dir):
        raise FileNotFoundError(f"Output directory {out_dir} does not exist.")
    if not os.path.isdir(out_dir):
        raise NotADirectoryError(f"Output directory {out_dir} is not a directory.")
    n_predictors = args.n_predictors
    data_lengths = args.data_lengths
    hist_lengths = args.hist_lengths
    n_epochs = args.n_epochs

    timing_fit = np.zeros((len(data_lengths), len(hist_lengths)))
    timing_not_fit = np.zeros((len(data_lengths), len(hist_lengths)))

    for i, dl in enumerate(data_lengths):
        for j, hl in enumerate(hist_lengths):
            taylor_look = hl // 2
            if taylor_look < 1:
                taylor_look = 1
            test_data = np.random.randn(10, dl)
            test_data = utilities.safe_standardize(test_data, 1)[0]
            test_predictors = np.random.randn(n_predictors, dl)
            test_predictors = utilities.safe_standardize(test_predictors, 1)[0]
            test_predictors = [tp for tp in test_predictors]
            start_time = time()
            miner = Mine(0.8, hl, -1, True, True, taylor_look, hl, False)
            miner.verbose = False
            miner.n_epochs = n_epochs
            miner.analyze_data(test_predictors, test_data)
            stop_time = time()
            timing_fit[i, j] = (stop_time - start_time) / 10
            # Not fit
            start_time = time()
            miner = Mine(0.8, hl, 1, True, True, taylor_look, hl, False)
            miner.verbose = False
            miner.n_epochs = n_epochs
            miner.analyze_data(test_predictors, test_data)
            stop_time = time()
            timing_not_fit[i, j] = (stop_time - start_time) / 10
            print(f"Completed timing on data length {dl} and history length {hl}.")

    df_fit = pd.DataFrame(timing_fit, index=data_lengths, columns=hist_lengths)
    df_not_fit = pd.DataFrame(timing_not_fit, index=data_lengths, columns=hist_lengths)

    df_fit.to_csv(os.path.join(out_dir, "timing_fit.csv"))
    df_not_fit.to_csv(os.path.join(out_dir, "timing_not_fit.csv"))