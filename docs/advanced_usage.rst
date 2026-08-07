Advanced code usage examples
=========================

All major classes and functions that make up MINE are readily importable into user code for advanced integration.

Import of MINE class for direct access to fit object:

.. code-block:: bash

    import neuro_mine as nm
    # load predictors and responses from desired files
    # predictors: List[n_timepoints long predictors]
    # responses: Array[n_responses x n_timepoints]
    # Note: At this level history and taylor look-ahead are provided in frames not time units
    miner = nm.Mine(train_fraction=2/3, model_history=50, score_cut=0.71, compute_taylor=True, return_jacobians=False,
                    taylor_look_ahead=25, taylor_pred_every=5, fit_spikes=False)
    mdata = miner.analyze_data(predictors, responses)
    # process mdata object in further code


In addition, the underlying CNN model can be imported directly:

.. code-block:: bash

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

To generate plots of autocorrelations of predictors and resposes, autocorrelation times, and pairwise correlations between predictors and responses, the following code can be run in the command line interface:

.. code-block:: bash

      Data-diagnostic -p <predictor files> -r <response files> -ut <to use time> -eps <if episodic> -o <output directory>
