"""
Script to convert Suite2p extracted activity into CSV format for MINE ingestion
"""

from PySide6.QtWidgets import QFileDialog, QApplication
import numpy as np
import pandas as pd
import argparse
from os import path
import os


if __name__ == '__main__':
    app = QApplication([])
    a_parser = argparse.ArgumentParser(prog="convert_suite2p.py",
                                       description="Converts suite2p output data to CSV format for MINE ingestion.")
    a_parser.add_argument("-d", "--s2pdir", help="Path to suite2p directory.", type=str)
    a_parser.add_argument("-isc", "--th_iscell", help="Threshold on suite2p classifier to consider "
                                                      "object as a neuron.", type=float, default=0.5)
    a_parser.add_argument("-ft", "--frame_time", help="Time between consecutive frames in same unit "
                                                      "as used for predictors. If not set suit2p value will be used.",
                          type=float)
    a_parser.add_argument("-dc", "--deconv", help="If set use deconvolved data instead of fluorescence.",
                          action='store_true')

    args = a_parser.parse_args()
    th_iscell = args.th_iscell
    frame_time = args.frame_time
    deconv = args.deconv
    s2pdir = args.s2pdir
    if s2pdir is None:
        s2pdir = QFileDialog.getExistingDirectory(caption="Please select suite2p output directory",
                                                  options=QFileDialog.DontUseNativeDialog)

    plane_dirs = os.listdir(s2pdir)
    plane_dirs = [path.join(s2pdir, d) for d in plane_dirs if path.isdir(path.join(s2pdir, d))] + [s2pdir]
    val_dirs = [d for d in plane_dirs if path.exists(path.join(d, "ops.npy"))]

    if len(val_dirs) == 0:
        app.quit()
        del app
        raise ValueError("Directory does not seem to be valid suite2p output."
                         "No subdirectories with output files found.")

    for vd in val_dirs:

        if frame_time is None:
            ops = np.load(path.join(vd, "ops.npy"), allow_pickle=True)
            fs = ops[()]["fs"]  # this is a frame-rate in Hz!
            ft = 1 / fs
        else:
            ft = frame_time

        # Suite2p saves the neural data such that neurons are index along axis 0
        # time is along axis 1 - we therefore need to transpose before saving
        if deconv:
            neuro_data = np.load(path.join(vd, "spks.npy"))
        else:
            neuro_data = np.load(path.join(vd, "F.npy"))

        iscell = np.load(path.join(vd, "iscell.npy"))[:, 1] > th_iscell

        neuro_data = neuro_data[iscell]

        time = np.arange(neuro_data.shape[1])*ft

        full_data = np.c_[time[:, None], neuro_data.T]

        col_names = ["time"] + [f"Neuron {i}" for i in range(neuro_data.shape[0])]

        full_data = pd.DataFrame(data=full_data, columns=col_names)

        full_data.to_csv(path.join(vd, "Neuron_data.csv"), index=False)

    app.quit()
    del app
