Data Requirements
=========================

    - Input file types: Any delimited file format such as comma-separated value, tab-separated value, etc. with time-varying data
    - All input files must be organized such that features are across columns and timepoints are across rows
    - Predictor data **must** have time as the first column; for easily interpretable outputs, predictor columns should be meaningfully labelled (e.g., 'temperature' or 'left_paw') in the header
    - Response data **must** have time as the first column and the responses must be in adjacent columns; column titles (a header) are supported but are not mandatory
    - Within episodes, data must be continuous in time, and time must be monotonically increasing
    - Common time encodings are supported but note that if times are recorded without dates and/or AM/PM designations, ordering of timepoints can be ambiguous.
    - Furthermore, time encoding **must** match between predictor and response files such that predictor times can be aligned with response times

.. note::
    ️Ambiguities in the time column will lead to failures; Be mindful of rounding when saving data to CSV which can assign the same time values to successive timepoints.
