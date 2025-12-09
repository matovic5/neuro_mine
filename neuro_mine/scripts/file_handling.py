import csv
from dateutil import parser as dateparser
import numpy as np
from os import path
from datetime import datetime, date, time
from typing import Optional, Tuple, List, Union
import os


def process_file_args(files_or_dir: List[str]) -> List[str]:
    """
    Processes file arguments, expanding directories if present
    :param files_or_dir: Path to file or directory or list of paths to files
    :return: List of file paths
    """
    # Note: We allow lists of files or a single file or a single directory but not lists containing directories
    if len(files_or_dir) == 1:
        if path.isdir(files_or_dir[0]):
            elements = os.listdir(files_or_dir[0])
            return [path.join(files_or_dir[0], e) for e in elements if path.isfile(path.join(files_or_dir[0], e)) and not e[0]=='.']
        elif path.isfile(files_or_dir[0]):
            return [files_or_dir[0]]
        else:
            raise ValueError("Unrecognized path: {}".format(files_or_dir))
    for f in files_or_dir:
        if not path.isfile(f):
            raise ValueError(f"{f} is not a path to a file. Note that if multiple arguments "
                             "are provided they have to be files")
    return files_or_dir


def pair_files(resp_files: List[str], pred_files: List[str]) -> List[Tuple[str, str]]:
    """
    Takes a list of response files and predictor files, matches them and then returns a list of matched tuples
    :param resp_files: List of response files
    :param pred_files: List of predictor files
    :return: Matched pairs
    """
    # At this moment we perform an extremely simple matching: We assume that the alphabetical order of predictor
    # and response files is the same
    if len(resp_files) != len(pred_files):
        raise ValueError(f"Cannot match {len(pred_files)} predictor files to {len(resp_files)} response files")
    resp_files = sorted(resp_files)
    pred_files = sorted(pred_files)
    return [(r, p) for r,p in zip(resp_files, pred_files)]


class FileParser:
    """
    Base class for file parser
    """
    def __init__(self, file_path):
        """
        Creates a new file parser object
        :param file_path: The path to the file to parse
        """
        if not path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found")
        if not path.isfile(file_path):
            raise FileNotFoundError(f"File {file_path} is not a file")
        self.filename = file_path

    @staticmethod
    def _parse_datetime(s: str) -> Optional[datetime]:
        """
        Tries to parse a datetime from a string
        :param s: The string to interpret as time
        :return: A datetime object or None if not a datetime input
        """
        # Check if the item can be converted to a floating-point number - if yes we treat it as "not a date"
        # and therefore return None
        try:
            float(s)
            return None  # not a date but a float
        except ValueError:
            pass
        try:
            return dateparser.parse(s)
        except (ValueError, OverflowError):
            return None  # neither a float nor a date - should we throw an exception here instead of returning None?

class CSVParser(FileParser):
    """
    Parser for CSV files
    """
    def __init__(self, file_path: str, prefix: str="col"):
        """
        Creates a new CSV file parser object
        :param file_path: The path to the file to parse
        :param prefix: If no column names are provided in the file this prefix will be used to label columns
        """
        super().__init__(file_path)
        self.delimiter = CSVParser._find_delimiter(self.filename)
        self.prefix = prefix

    @staticmethod
    def _find_delimiter(filename):
        sniffer = csv.Sniffer()
        with open(filename) as fp:
            delimiter = sniffer.sniff(fp.read(-1)).delimiter
        return delimiter

    def load_data(self) -> Tuple[np.ndarray, bool, List]:
        """
        Loads the data from the file
        :return:
        """
        # Load as text-file, processing line-by-line
        with open(self.filename, "r") as f:
            lines = f.readlines()

        # Identify number of header rows - these can be rows that contain actual column headers
        # or rows with descriptive text. In other words we try to find the first true data-row here
        # using simple heuristics which will likely break if the user supplies pathological files
        skip = 0  # counter of how many rows to skip as header
        ncols = None  # the number of actual data columns
        header_row = None  # the column labels

        # Detect where numeric data starts
        for line in lines:
            parts = line.strip().split(self.delimiter)
            # the first column has to contain time, however this can be either floating points
            # counting seconds/minutes/etc or actual time objects
            first_col = self._parse_datetime(parts[0])

            if first_col is not None:  # datetime in first column
                try:
                    [float(x) for x in parts[1:] if x != ""]
                    ncols = len(parts)
                    break
                except ValueError:
                    skip += 1  # the row contained a non-numerical object and is therefore considered a header
            else:  # try full row as floats, since time should be numerical
                try:
                    [float(x) for x in parts if x != ""]
                    ncols = len(parts)
                    break
                except ValueError:
                    skip += 1

        # Try to find column header definition in skipped rows - this should be a row
        # that has the same number of columns as the data
        assert ncols is not None
        if skip > 0:
            for i in range(skip - 1, -1, -1):
                parts = lines[i].strip().split(self.delimiter)
                if len(parts) == ncols:
                    header_row = parts
                    break

        # assemble all lines that have a full column count
        numeric_part = [line.strip().split(self.delimiter) for line in lines[skip:]]
        numeric_part = [row for row in numeric_part if len(row) == ncols]

        data = []
        # determine how time is saved within the file
        first_val = self._parse_datetime(numeric_part[0][0])
        first_is_datetime = first_val is not None

        if first_is_datetime:
            # In the following we want to recode time into a count of seconds relative to a start time
            # since we do not know when predictors recording started relative to response acquisition
            # this start time has to be independent of the timestamp itself. However, it shouldn't be
            # so far in the past that we lose resolution. Arbitrarily, we chose the millennium
            # The better way would clearly be to find the minimum of predictor and response start times
            # and use that value but that can only happen after file matching
            t0 = datetime.combine(date(2000, 1, 1), time())
            for row in numeric_part:
                t = self._parse_datetime(row[0])
                ts = (t - t0).total_seconds()
                rest = [float(x) if x != "" else np.nan for x in row[1:]]
                data.append([ts] + rest)
        else:
            for row in numeric_part:
                data.append([float(x) if x != "" else np.nan for x in row])

        data = np.array(data, dtype=float)
        data_has_header = header_row is not None

        # Make sure that the first column can be interpreted as time
        if any(np.diff(data[:, 0]) <= 0):
            raise ValueError("First column in datafile should be time, but values aren't strictly increasing")

        if data_has_header:
            data_header = header_row
        else:
            ncols = data.shape[1]
            # The name of the first column is Time
            data_header = ["Time"]+[f"{self.prefix}_{i}" for i in range(ncols-1)]

        # remove rows that contain NaN values
        has_nan = np.sum(np.isnan(data), axis=1) > 0
        data = data[np.logical_not(has_nan)]

        return data, data_has_header, data_header