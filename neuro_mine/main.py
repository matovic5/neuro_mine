"""
Module for easy running of MINE on user data
"""

import subprocess
import importlib.resources
import sys

def main_gui():
    with importlib.resources.path("neuro_mine.scripts", "app_gui.py") as script_path:
        subprocess.run(["python", str(script_path)])

def main():
    with importlib.resources.path("neuro_mine.scripts", "process_csv.py") as script_path:
        if len(sys.argv) > 1:
            subprocess.run(["python", str(script_path)] + sys.argv[1:])
        else:
            subprocess.run(["python", str(script_path)])