import argparse
from datetime import datetime
from neuro_mine.lib.processing import process_paired_files
import json
import os
from os import path
import neuro_mine.lib.file_handling as fh
from neuro_mine.lib.options import default_options


class MineException(Exception):
    def __init__(self, message):
        super().__init__(message)


class ConfigException(Exception):
    def __init__(self, message):
        super().__init__(message)


if __name__ == '__main__':

    # the following will prevent tensorflow from using the GPU - as the used models have very low complexity
    # they will generally be fit faster on the CPU - furthermore parallelization currently used
    # will not work if tensorflow is run on the GPU!!
    os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

    a_parser = argparse.ArgumentParser(prog="Mine",
                                       description="Uses MINE to fit and interpret CNN models that relate predictors"
                                                   "identified by one CSV file to responses identified by another.")
    # Files and directories - required no defaults
    a_parser.add_argument("-p", "--predictors", help="Path to CSV files of predictors or alternatively "
                                               "directory with predictor files.",
                    type=str, required=True, nargs='+')
    a_parser.add_argument("-r", "--responses", help="Path to CSV files of responses or alternatively "
                                              "directory with response files.",
                    type=str, required=True, nargs='+')
    a_parser.add_argument("-od", "--outdir", help="Path to model output directory.", type=str, required=True)
    a_parser.add_argument("-o", "--config", help="Path to config file with run parameters.", type=str, default=None)

    # Run parameters with default values - if not set on command line will be drawn from either provided options
    # file or default options
    a_parser.add_argument("-mh", "--history", help="The length of model history in time units.",
                          type=float, default=None)

    a_parser.add_argument("-mtf", "--miner_train_fraction", help="The fraction of data to use for training",
                          type=float, default=None)

    a_parser.add_argument("-dsf", "--downsampling", help="The downsampling factor",
                          type=int, default=None)
    a_parser.add_argument("-tl", "--taylor_look", help="Determines taylor look ahead as multiplier of history",
                          type=float, default=None)
    a_parser.add_argument("-e", "--n_epochs", help="Number of epochs when fitting model.", type=int,
                          default=None)

    # Analysis parameters with default values - if not set on command line will be drawn from either provided options
    # file or default options
    a_parser.add_argument("-ct", "--th_test", help="The test score threshold to "
                                                   "decide that fit was successful.",
                          type=float, default=None)
    a_parser.add_argument("-ts", "--taylor_sig", help="The significance threshold for taylor expansion.",
                          type=float, default=None)
    a_parser.add_argument("-tc", "--taylor_cut", help="The variance fraction that has to be lost to"
                                                      "consider component important for fit.",
                          type=float, default=None)
    a_parser.add_argument("-la", "--th_lax", help="The threshold of variance explained by the linear"
                                                  "approximation to consider the fit linear.",
                          type=float, default=None)
    a_parser.add_argument("-lsq", "--th_sqr", help="The threshold of variance explained by the 2nd order"
                                                   "approximation to consider the fit 2nd order.",
                          type=float, default=None)

    # Various flags - these are false by default, will be set to true if indicated in options file
    a_parser.add_argument("-ut", "--use_time", help="If set time will be used as one predictor.",
                    action='store_true')
    a_parser.add_argument("-eps", "--episodic", help="If set data is assumed to be episodic with one "
                                                     "predictor and one response file per episode.",
                          action="store_true")
    a_parser.add_argument("-sh", "--run_shuffle", help="If set shuffled controls will be run as well.",
                          action='store_true')
    a_parser.add_argument("-j", "--jacobian", help="Store the Jacobians (linear receptive fields) for each response.",
                          action='store_true')
    a_parser.add_argument("-mq", "--miner_quiet", help="Do not receive updates on model fitting in command line",
                          action='store_true')
    a_parser.add_argument("-imw", "--ignore_mem", help="If set, memory warning for data will be ignored "
                                                       "otherwise program will stop if memory might be insufficient.",
                          action="store_true")
    a_parser.add_argument("-z", "--train_progress", help="If set, training progress across episodes will"
                                                         " be saved and plotted.",
                          action="store_true")

    args = a_parser.parse_args()

    # Deal with path-type arguments
    r_paths = fh.process_file_args(args.responses)
    p_paths = fh.process_file_args(args.predictors)

    file_pairs = fh.pair_files(r_paths, p_paths)

    if not os.path.exists(args.outdir):
        raise FileNotFoundError(f"Output directory {args.outdir} does not exist.")
    if not os.path.isdir(args.outdir):
        raise NotADirectoryError(f"Output directory {args.outdir} is not a directory.")

    # determine whether a provided config file or the default options will form the basis of the parameters
    # Note: Parameters set on command line will always override what is provided in config file!
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
    # in case the config file of an older version was loaded, supplement with default keys where necessary:
    for k in default_options:
        if k not in config_dict:
            config_dict[k] = default_options[k]

    # set flag values
    if args.use_time or config_dict["use_time"]:
        time_as_pred = True
    else:
        time_as_pred = False
    if args.episodic or config_dict["episodic"]:
        is_episodic = True
    else:
        is_episodic = False
    if args.run_shuffle or config_dict["run_shuffle"]:
        run_shuffle = True
    else:
        run_shuffle = False
    if args.jacobian or config_dict["jacobian"]:
        fit_jacobian = True
    else:
        fit_jacobian = False
    miner_verbose = False if args.miner_quiet else True
    if args.ignore_mem or config_dict["ignore_memory_warning"]:
        ignore_mem = True
    else:
        ignore_mem = False
    if args.train_progress or config_dict["train_progress"]:
        train_progress = True
    else:
        train_progress = False

    # set valued parameters
    history = config_dict["history"] if args.history is None else args.history
    miner_train_fraction = config_dict["miner_train_fraction"] if args.miner_train_fraction is None else args.miner_train_fraction
    downsampling = config_dict["downsampling"] if args.downsampling is None else args.downsampling
    taylor_look = config_dict["taylor_look"] if args.taylor_look is None else args.taylor_look
    taylor_sig = config_dict["taylor_sig"] if args.taylor_sig is None else args.taylor_sig
    n_epochs = config_dict["n_epochs"] if args.n_epochs is None else args.n_epochs
    th_test = config_dict["th_test"] if args.th_test is None else args.th_test
    taylor_cut = config_dict["taylor_cut"] if args.taylor_cut is None else args.taylor_cut
    th_lax = config_dict["th_lax"] if args.th_lax is None else args.th_lax
    th_sqr = config_dict["th_sqr"] if args.th_sqr is None else args.th_sqr

    if len(file_pairs) < 2:
        # avoids bug in processing single files as episodic data
        is_episodic = False

    # set up shared part of configuration
    configuration = {
        "config":
            {
                "use_time": time_as_pred,
                "run_shuffle": run_shuffle,
                "th_test": th_test,
                "taylor_sig": taylor_sig,
                "taylor_cut": taylor_cut,
                "th_lax": th_lax,
                "th_sqr": th_sqr,
                "history": history,
                "taylor_look": taylor_look,
                "jacobian": fit_jacobian,
                "n_epochs": n_epochs,
                "miner_verbose": miner_verbose,
                "miner_train_fraction": miner_train_fraction,
                "downsampling": downsampling,
                "ignore_memory_warning": ignore_mem,
                "train_progress": train_progress,
            },
        "run":
            {
                "outdir": args.outdir,
                "timestamp": datetime.now().isoformat(),
            }
    }

    if not is_episodic:
        for i, pair in enumerate(file_pairs):
            # add files to config information
            configuration["run"]["predictor_file"] = pair[1]
            configuration["run"]["response_file"] = pair[0]


            ###
            # Load and process data
            ###
            process_paired_files([pair[0]], [pair[1]], configuration)
    else:
        r_files = [pair[0] for pair in file_pairs]
        p_files = [pair[1] for pair in file_pairs]
        # add files to config information
        configuration["run"]["predictor_files"] = p_files
        configuration["run"]["response_files"] = r_files

        process_paired_files(r_files, p_files, configuration)