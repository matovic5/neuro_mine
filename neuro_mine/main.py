"""
Module for easy running of MINE on user data
"""

import subprocess
import importlib.resources
import sys

def main():
    with importlib.resources.path("neuro_mine.scripts", "neuromine_fit.py") as script_path:
        if len(sys.argv) > 1:
            subprocess.run(["python", str(script_path)] + sys.argv[1:])
        else:
            with importlib.resources.path("neuro_mine.ui", "fit_gui.py") as script_path:
                subprocess.run(["python", str(script_path)])


def predict():
    with importlib.resources.path("neuro_mine.scripts", "neuromine_prediction.py") as script_path:
        if len(sys.argv) > 1:
            subprocess.run(["python", str(script_path)] + sys.argv[1:])
        else:
            with importlib.resources.path("neuro_mine.ui", "predict_gui.py") as script_path:
                subprocess.run(["python", str(script_path)])