import numpy as np

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
    "miner_verbose": True,
    "miner_train_fraction": 0.8,
    "episodic": False,
    "downsampling": 1,
}
