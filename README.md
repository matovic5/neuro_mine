# Neuro-MINE (Model Identification of Neural Encoding) 🧠💻

Welcome to Neuro-MINE: your handy companion for processing neuronal response data! This app allows users to use MINE as a GUI or in the command line to train a flexible, convolutional neural network (CNN) to analyze experimental datasets containing neural activity and corresponding predictors (e.g., behavioral responses).

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

<details>
  <summary><strong>Use Cases and Requirements</strong></summary>

  <p><strong>Use Cases:</strong></p>
  <ul>
    <li>Any model organism</li>
    <li>Any type of predictor data (stimuli and/or behavior)</li>
    <li>Any type of response data (imaging or spikes)</li>
    <li>Episodic or non-episodic data</li>
    <li>Generate response predictions from new predictors use an existing model</li>
  </ul>

  <p><strong>Data Requirements:</strong></p>
  <ul>
    <li>File type: .csv with any delimiter</li>
    <li>Predictor data **must** have time as the first column and it must be named 'time'; for optimal outputs, predictor columns should be meaningfully labelled (e.g., 'temperature' or 'left_paw') in the header</li>
    <li>Reponse data **must** have time as the first column and the responses must be in adjacent columns; column titles (a header) are supported but are not mandatory</li>
    <li>Within episodes, data must be continuous in time, and time must be monotonically increasing</li>
  </ul>
</details>

<details>
<summary><strong>Neuro-MINE for Fitting</strong></summary>

To launch GUI for model fitting:
```bash
Mine-gui
```

Possible commmand line arguments for fitting with Neuro-MINE:
```bash
Mine -p <predictor directory or filepath(s)> -r <respose directory or filepath(s)> -ut <use time> -sh <run shuffle> -ct <test score threshold> -ts <Taylor significance> -la <linear fit variance fraction> -lsq <square fit variance fraction> -n <name of model> -mh <model history (seconds)> -tl <Taylor lookahead> -j <Store Jacobians> -o <JSON filepath with existing parameters>  -e <epoch number> -mv <verbose in terminal> -mtf <fraction of data for training vs testing> -eps <data is eposidic>
```

```bash
Mine --help # see possible command line prompts to customize the model
```

</details>

<details>
<summary><strong>Neuro-MINE for Predictions</strong></summary>

To launch GUI for response prediction:
```bash
Mine-predict # Launches prediction GUI from existing models and new prediction data
```

Possible commmand line arguments for predicting with Neuro-MINE:
```bash
Mine-predict -p <predictor directory or filepath(s)> -o <JSON filepath with model parameters> -w <hdf5 filepath with weights> -a <hdf5 filepath with analysis of fit> -ct <test score threshold>
```

```bash
Mine-predict --help # see possible command line prompts to parameterize the prediction
```

</details>

*Authors:*
<br>Danica Matovic
<br>Martin Haesemeyer
<br>Jamie Costabile
<br>Kaarthik Balakrishnan
<br>Sina Schwinn

*Publication:* Costabile JD, Balakrishnan KA, Schwinn S, Haesemeyer M. Model discovery to link neural activity to behavioral tasks. Elife. 2023 Jun 6;12:e83289. doi: 10.7554/eLife.83289. PMID: 37278516; PMCID: PMC10310322. https://elifesciences.org/articles/83289

*GitHub Repository of Original Publication:* https://github.com/haesemeyer/mine_pub
<br>*Lab Website:* https://www.thermofish.org/

All code is licensed under the MIT license. See LICENSE for details.
<br>© Martin Haesemeyer, Jamie D Costabile, Kaarthik A Balakrishnan, and Danica Matovic 2020-2025
<br> Questions may be directed to haesemeyer.1@osu.edu
