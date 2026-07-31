import csv
from dateutil import parser as dateparser
import numpy as np
from os import path
from datetime import datetime, date, time
from typing import Optional, Tuple, List
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
        self.delimiter = self._find_delimiter()
        self.col_count = self._validate_file_contents()
        if self.col_count == -1:
            raise IOError("CSV file has different column counts across rows. Please ensure that all rows have the same number of columns.")
        self.prefix = prefix

    def _find_delimiter(self):
        sniffer = csv.Sniffer()
        with open(self.filename) as fp:
            delimiter = sniffer.sniff(fp.read(-1)).delimiter
        return delimiter

    def _validate_file_contents(self) -> int:
        """
        Performs basic validation of file contents to ensure that all rows within the file have the same number of components
        :return: Number of columns if validated otherwise -1
        """
        with open(self.filename, "r") as f:
            lines = f.readlines()
        col_count = None
        for l in lines:
            if col_count is None:
                col_count = len(l.strip().split(self.delimiter))
            else:
                if col_count != len(l.strip().split(self.delimiter)):
                    return -1
        return col_count

    def _load_date_column(self, column: List[str], col_name: int) -> np.ndarray:
        """
        Loads a column with encoded dates/times and encodes them as seconds elapsed since the millennium start such that
        they can be properly related for interpolation across files
        :param column: The file column
        :param col_name: The name of the column
        :return: The date-time-values encoded as seconds since the millennium start
        """
        retval = np.full((len(column), 1), np.nan)
        # In the following we want to recode time into a count of seconds relative to a start time
        # since we do not know when predictors recording started relative to response acquisition
        # this start time has to be independent of the timestamp itself. However, it shouldn't be
        # so far in the past that we lose resolution. Arbitrarily, we chose the millennium
        # The better way would clearly be to find the minimum of predictor and response start times
        # and use that value but that can only happen after file matching
        t0 = datetime.combine(date(2000, 1, 1), time())
        for i, elem in enumerate(column):
            # we skip empty cells
            if elem.strip() == "":
                continue
            t = self._parse_datetime(elem)
            if t is None:
                raise ValueError(f"Column {col_name} was identified as containing date-time information but contains "
                                 f"mixed content which is not supported. This can be caused by ambiguous encoding or "
                                 f"misidentification of a malformed header.")
            t_seconds = (t - t0).total_seconds()
            retval[i] = t_seconds
        return retval

    @staticmethod
    def _load_string_column(column: List[str], col_name: int) -> np.ndarray:
        """
        Loads a column with text and interprets unique strings as categories
        :param column: The file column
        :param col_name: The name of the column
        :return: The categories encoded as integers
        """
        retval = np.full((len(column), 1), np.nan)
        categ_dict = {}
        categ_count = 0
        for i, elem in enumerate(column):
            # we skip empty cells
            if elem.strip() == "":
                continue
            valid = False
            try:
                float(elem)
            except ValueError:
                valid = True
            if not valid:
                raise ValueError(f"Column {col_name} was identified as containing text but contains at least one number."
                                 f"Mixed content is not supported. This can be caused by ambiguous encoding or "
                                 f"misidentification of a malformed header.")
            if elem not in categ_dict:
                categ_dict[elem] = categ_count
                categ_count += 1
            retval[i] = categ_dict[elem]
        if categ_count > 2:
            print("###", flush=True)
            print(f"Column {col_name} was interpreted as categorical data with {categ_count} categories. Processing will"
                  f" continue, however, categorical inputs are not properly supported.", flush=True)
            print("###", flush=True)
        return retval

    @staticmethod
    def _load_numerical_column(column: List[str], col_name: int) -> np.ndarray:
        """
        Loads a column with (floating point) numbers
        :param column: The file column
        :param col_name: The name of the column
        :return: The numerical data as floating point numbers
        """
        retval = np.full((len(column), 1), np.nan)
        for i, elem in enumerate(column):
            # we skip empty cells
            if elem.strip() == "":
                continue
            try:
                value = float(elem)
            except ValueError:
                raise ValueError(
                    f"Column {col_name} was identified as containing numerical data but contains at least one text item."
                    f"Mixed content is not supported. This can be caused by ambiguous encoding or "
                    f"misidentification of a malformed header.")
            retval[i] = value
        return retval

    def load_data(self) -> Tuple[np.ndarray, bool, List]:
        """
        Loads the data from the file
        :return:
        """
        # We allow at most one header row - so we simply ask csv sniffer if there is a header or not
        sniffer = csv.Sniffer()
        with open(self.filename) as f:
            has_header = sniffer.has_header(f.read(-1))

        # Load as text-file, processing line-by-line
        with open(self.filename, "r") as f:
            lines = f.readlines()

        # Determine data header (column names)
        if has_header:
            data_header = lines[0].strip().split(self.delimiter)
            skip = 1  # skip first row when loading data
        else:
            # The name of the first column is Time
            data_header = ["Time"]+[f"{self.prefix}_{i}" for i in range(self.col_count-1)]
            skip = 0

        # assemble all lines that contain data, split by the delimiter
        file_contents = [line.strip().split(self.delimiter) for line in lines[skip:]]

        # reorganize data into individual columns
        file_columns = []
        for i in range(self.col_count):
            file_columns.append([d[i] for d in file_contents])

        # assemble converted numerical data
        data_columns = []
        for i, dc in enumerate(file_columns):
            # determine if column contains: (a) a datetime, (b) a float, (c) a string
            t = self._parse_datetime(dc[0])
            if t is not None:
                data_columns.append(self._load_date_column(dc, i))
                continue
            try:
                float(dc[0])
            except ValueError:
                data_columns.append(self._load_string_column(dc, i))
                continue
            data_columns.append(self._load_numerical_column(dc, i))


        data = np.hstack(data_columns)

        # Make sure that the first column can be interpreted as time
        if any(np.diff(data[:, 0]) <= 0):
            raise ValueError("The first column in each datafile should be time. However values aren't strictly increasing,"
                             " which means that data cannot be assigned to unique timepoints.")

        # remove columns that contain all NaN - these can occur when cell contents in CSV files
        # are deleted without deleting the column itself
        full_nan = np.sum(np.isnan(data), axis=0) == data.shape[0]
        data_header = [dh for i, dh in enumerate(data_header) if not full_nan[i]]
        data = data[:, np.logical_not(full_nan)]

        # remove rows that contain at leat one NaN value
        has_nan = np.sum(np.isnan(data), axis=1) > 0
        if np.sum(has_nan) > 0:
            print("###", flush=True)
            print(f"Removed {np.sum(has_nan)} rows from {self.filename} since they contained at least one NaN or a missing value.", flush=True)
            print("Note, deleting rows from within Microsoft Excel will sometimes remove data but leave ghost rows in the file. These will trigger this warning as well.")
            print("###", flush=True)
        data = data[np.logical_not(has_nan)]

        return data, has_header, data_header