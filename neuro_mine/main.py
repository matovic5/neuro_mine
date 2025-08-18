"""
Module for easy running of MINE on user data
"""

import subprocess
import importlib.resources
import sys

def main():
    # Find the path to the script within the package
    with importlib.resources.path("neuro_mine.scripts", "process_csv.py") as script_path:
        if len(sys.argv) > 1:
            subprocess.run(["python", str(script_path)] + sys.argv[1:])
        else:
            subprocess.run(["python", str(script_path)])