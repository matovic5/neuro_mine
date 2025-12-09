import argparse
from datetime import datetime
from processing import process_paired_files
import json
import numpy as np
import os
from os import path
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
    a_parser.add_argument("-p", "--predictors", help="Path to CSV files of predictors or alternatively "
                                                     "directory with predictor files.",
                          type=str, required=True, nargs='+')
    a_parser.add_argument("-r", "--responses", help="Path to CSV files of responses or alternatively "
                                                    "directory with response files.",
                          type=str, required=True, nargs='+')
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
    a_parser.add_argument("-eps", "--episodic", help="If set data is assumed to be episodic with one "
                                                     "predictor and one response file per episode.",
                          action="store_true")

    args = a_parser.parse_args()

    is_episodic = args.episodic

    r_paths = fh.process_file_args(args.responses)
    p_paths = fh.process_file_args(args.predictors)

    file_pairs = fh.pair_files(r_paths, p_paths)

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

    if not is_episodic:
        for i, pair in enumerate(file_pairs):
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
                        "model_name": your_model if len(file_pairs)==1 else f"{your_model}_{i}",
                        "predictor_file": pair[1],
                        "response_file": pair[0],
                        "timestamp": datetime.now().now().isoformat(),
                    }
            }


            ###
            # Load and process data
            ###
            process_paired_files([pair[0]], [pair[1]], configuration)
    else:
        r_files = [pair[0] for pair in file_pairs]
        p_files = [pair[1] for pair in file_pairs]
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
                    "predictor_files": p_files,
                    "response_files": r_files,
                    "timestamp": datetime.now().now().isoformat(),
                }
        }
        process_paired_files(r_files, p_files, configuration)
