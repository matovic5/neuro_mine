# Neuro-MINE (Model Identification of Neural Encoding) 🧠💻

Welcome to Neuro-MINE: your handy companion for processing neuronal response data!

This app allows users to use MINE as a GUI or in the command line to train a flexible,
convolutional neural network (CNN) to analyze experimental datasets containing neural
activity and corresponding predictors (e.g., behavioral responses).

Neuro-MINE makes an updated version of MINE ([Costabile et al., 2023](https://elifesciences.org/articles/83289))
available in an easy-to-use interface.
This version of MINE now supports spiking data as well as episodic data.
For episodic data, care is taken that model fits, Taylor decomposition, and prediction correctly
handle episode boundaries.
Furthermore, Neuro-MINE provides easily interpretable outputs in a model insights file that can be used as
starting points for further analysis.

# Installation
The examples below use conda to manage environments but any environment manager or python installation will work.

[1] Create an environment using Python v3.9
Note: If this step is skipped to use an existing environment, Tensorflow>2.15.1 should not already be installed.

```bash
conda create -n mine python=3.9
```

[2] Activate new environment

```bash
conda activate mine
```

[3] Install/upgrade Neuro-MINE from PyPi

```bash
pip install -U neuro_mine
```

<details>
  <summary><strong>Use Cases and Requirements</strong></summary>

  <p><strong>Use Cases:</strong></p>
  <ul>
    <li>Any model organism</li>
    <li>Any type of predictor data (stimuli and/or behavior)</li>
    <li>Any type of response data (imaging or spikes)</li>
    <li>Episodic or non-episodic data</li>
    <li>Generate response predictions from new predictors using an existing model</li>
    <li>While all descriptions reference neurons, neuro-mine can process any time-varying data</li>
  </ul>

  <p><strong>Data Requirements:</strong></p>
  <ul>
    <li>File type: .csv with any delimiter</li>
    <li>Predictor data **must** have time as the first column and it must be named 'time'; for optimal outputs, predictor columns should be meaningfully labelled (e.g., 'temperature' or 'left_paw') in the header</li>
    <li>Reponse data **must** have time as the first column and the responses must be in adjacent columns; column titles (a header) are supported but are not mandatory</li>
    <li>Within episodes, data must be continuous in time, and time must be monotonically increasing</li>
    <li>⚠️Please note that ambiguities in the time column will lead to failures:
            <ul>
            <li>Be mindful of rounding when saving
                data to CSV which can assign the same time values to successive timepoints.
            </li>
            <li> Common time encodings are supported but note that if times are recorded without dates and/or AM/PM
                designations, ordering of timepoints will be ambiguous.
            </li>
            </ul>
    </li>
  </ul>
</details>

<details>
<summary><strong>Neuro-MINE for Training</strong></summary>

To launch GUI for model training:
```bash
Mine
```

Possible commmand line arguments for fitting with Neuro-MINE:
```bash
Mine -p <predictor directory or filepath(s)> -r <respose directory or filepath(s)> -ut <use time> -sh <run shuffle> -ct <test score threshold> -ts <Taylor significance> -la <linear fit variance fraction> -lsq <square fit variance fraction> -n <name of model> -mh <model history (seconds)> -tl <Taylor lookahead> -j <Store Jacobians> -o <JSON filepath with existing parameters>  -e <epoch number> -mq <non-verbose in terminal> -mtf <fraction of data for training vs testing> -eps <data is eposidic>
```

```bash
Mine --help # see possible command line prompts to customize the model
```

Neuro-MINE Train GUI Documentation:
<img width="3456" height="1665" alt="GUI-train-README" src="https://github.com/user-attachments/assets/2158c3b9-3bb1-4a9d-8911-2bcba4455125" />

Neuro-MINE Parameter Documentation:
<table>
  <thead>
    <tr>
      <th>Name</th>
      <th>Explanation</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Test Score Threshold [-ct] </td>
      <td>
        <p>Sets the minimal correlation between model predictions and true outcomes needed on test data to consider a response “fit.” Changing this value will have the greatest influence on results because it will filter responses whose test correlation is below the set threshold.</p>
        <p>Currently set to the square root of 0.5 (√0.5), which indicates that the prediction explains 50 % of the variance in the data. Empirically, this threshold yielded a >90-fold enrichment of true over false positives.</p>
      </td>
    </tr>
    <tr>
      <td>Model History [-mh]</td>
      <td>
        <p>Number of seconds of past data to be used for fitting (higher history increases runtime). This value should be set based on expectations around how far in the past events might influence current neural activity.
Note: Currently, inputs to the model are limited to past events, however, for motor outputs, anticipatory activity could be of interest which would require future inputs or a negative value for history. While this isn’t supported, a similar effect can be achieved by time-shifting the predictors relative to the responses, see Costabile et al., 2023.</p>
      </td>
    </tr>
    <tr>
      <td>Number of Epochs [-e]</td>
      <td>
        <p>Number of iterations with which the model will be fit over the entirety of the training data.</p>
        <p>Current default is 100 for an intermediate size data set; the larger the data set, the less epochs will be needed to find patterns in it, and vice versa.</p>
      </td>
    </tr>
    <tr>
      <td>Train Data Fraction [-mtf]</td>
      <td>
        <p>Fraction of data to be used for training (remaining value to 1.0 will be used for testing).</p>
        <p><i>Note on generalization:</i> If the input data is periodic, test score correlations will still speak to the quality of fit, but to test whether the model generalizes, predictors in the test period should be different than predictors in the training period.</p>
        <p><i>Note on episodic data:</i> Train/test sets are split by episodes. In other words, if the experiment contains 10 episodes, then the first 8 will be used for training, the last 2 for testing at the default value.</p>
      </td>
    </tr>
    <tr>
      <td>Cutoff [-tc]</td>
      <td>
        <p>Minimal fraction of variance explained that needs to be lost for a predictor to be considered driving a response. A value of 0.1 is a sensible default if neurons robustly respond to their inputs. If responses are expected to be stochastic, a value of 0 is more sensible.</p>
      </td>
    </tr>
    <tr>
      <td>Significance Threshold [-ts]</td>
      <td>
        <p>The loss in explained variance, after correcting for multiple comparisons, has to be significantly larger than “Cutoff” at this p-value for a predictor to be considered driving a response.</p>
      </td>
    </tr>
      <tr>
      <td>Look Ahead [-tl]</td>
      <td>
        <p>As a fraction of model history, the number of timepoints into the future that will be predicted by the Taylor expansion. Raising this value significantly will overall decrease the fidelity of the Taylor expansion prediction, leading to unstable assignments of predictors to responses. Lowering the value close to 0, improves the prediction, but again decreases stability, since predictions often become trivial.</p>
      </td>
    </tr>
    <tr>
      <td>Linear Fit Variance Fraction [-la]</td>
      <td>
        <p>Threshold on the fraction of variance explained by a linear expansion of the model. If this threshold is crossed, the neural response is considered “linear.”</p>
      </td>
    </tr>
      <tr>
      <td>Square Fit Variance Fraction [-lsq]</td>
      <td>
        <p>Threshold on the fraction of variance explained by a 2nd order expansion of the model. If this threshold is crossed, and the linear threshold is not, the neural response is considered 2nd order (reported as “square” in insights). If neither is crossed it will be reported as “cubic+” and is considered of higher order than 2.</p>
      </td>
    </tr>
  </tbody>
</table>

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

Neuro-MINE Predict Documentation: 
<img width="1694" height="1090" alt="GUI-predict-README" src="https://github.com/user-attachments/assets/6e5ddd5b-edb5-4ae2-aa40-af3c44a92ce4" />

</details>

<details>
<summary><strong>Advanced code usage examples</strong></summary>
All major classes and functions that make up MINE are readily importable into user code for advanced integration.

Import of MINE class for direct access to fit object:
```python
import neuro_mine as nm
# load predictors and responses from desired files
# predictors: List[n_timepoints long predictors]
# responses: Array[n_responses x n_timepoints]
# Note: At this level history and taylor look-ahead are provided in frames not time units
miner = nm.Mine(train_fraction=2/3, model_history=50, score_cut=0.71, compute_taylor=True, return_jacobians=False,
                taylor_look_ahead=25, taylor_pred_every=5, fit_spikes=False)
mdata = miner.analyze_data(predictors, responses)
# process mdata object in further code
```

In addition, the underlying CNN model can be imported directly:
```python
import neuro_mine as nm
# Note: input_length is the same as model history
# This approach allows customizing the complexity of the model
model = nm.ActivityPredictor(n_units=1024, n_conv=150, drop_rate=0.5, input_length=50, activation="swish",
                             predict_spikes=True)
# Note: the datacount input is unused
nm.train_model(model, train_data, n_epochs=50, datacount=0)
# Further processing on model object, e.g. calculating linear derivative of the output with respect
# to all inputs in the neighborhood of X0
nm.dca_dr(model, X0)
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
