# Model Identification of Neural Encoding (MINE) 🧠💻

This program allows users to use MINE to train a flexible convolutional neural network (CNN) to analyze experimental datasets containing neural activity and corresponding predictors (e.g., behavioral responses).

*Authors:*
<br>Dr. Martin Haesemeyer
<br>Jamie Costabile
<br>Dr. Kaarthik Balakrishnan
<br>Sina Schwinn
<br>Danica Matovic

*Publication:* Costabile JD, Balakrishnan KA, Schwinn S, Haesemeyer M. Model discovery to link neural activity to behavioral tasks. Elife. 2023 Jun 6;12:e83289. doi: 10.7554/eLife.83289. PMID: 37278516; PMCID: PMC10310322. https://elifesciences.org/articles/83289

*GitHub Repository of Original Publication:* https://github.com/haesemeyer/mine_pub
<br>*Lab Website:* https://www.thermofish.org/

All code is licensed under the MIT license. See LICENSE for details.
<br>© Martin Haesemeyer, Jamie D Costabile, Kaarthik A Balakrishnan, and Danica Matovic 2020-2025
<br> Questions may be directed to haesemeyer.1@osu.edu

# Quick Start

[1] Create an environment using Python v3.9

```bash
conda create -n mine python=3.9
```

[2] Activate new environment

```bash
conda activate mine
```

[3] Install MINE from PyPi

```bash
pip install neuro_mine
```

[4] Run program

```bash
Mine
```

[5] Follow dialog prompts to select predictors and response .csv files. These files must have the following structure:
<br>- .csv file format
<br>- Predictor data **must** have time as the first column and it must be named 'time'; for optimal outputs, predictor columns should be meaningfully labelled (e.g., 'temperature' or 'left_paw') in the header
<br>- Reponse data **must** have time as the first column and the responses must be in adjacent columns; column titles (a header) are supported but are not mandatory

*Application:*
<br>- Any model organism
<br>- Any type of predictor data (stimuli and/or behavior)
<br>- Any type of response data (imaging or spikes)


*Limitation:*
<br>- Data must be continuous in time, and time must be monotonically increasing (i.e., any discontinuity between epochs must be resolved prior to fitting)
