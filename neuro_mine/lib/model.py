"""
Module for all network models with tensorflow dependency
"""
import numpy as np
import os
os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GLOG_minloglevel"] = "2"
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
import tensorflow as tf

tf.get_logger().setLevel("ERROR")
import tensorflow.keras as keras
from tensorflow.keras import layers, regularizers, initializers
from typing import Optional, Union
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)


class NotInitialized(Exception):
    def __init__(self, message):
        super().__init__(message)


class ActivityPredictor(keras.Model):
    """
    Simple network for non-linear prediction of calcium activity
    """

    def __init__(self, n_units: int, n_conv: int, drop_rate: float, input_length: int, activation: str,
                 predict_spikes: bool):
        """
        Creates a new NetNavigator
        :param n_units: The number of units in each dense layer
        :param n_conv: The number of units in each initial convolutional layer
        :param drop_rate: The drop-out rate during training
        :param input_length: The length (across time) of inputs to the network (sets conv filter size)
        :param activation: The activation function to use
        :param predict_spikes: If true, 0/1 spike data instead of continuous data is expected
        """
        super(ActivityPredictor, self).__init__()
        if drop_rate < 0 or drop_rate > 1:
            raise ValueError("drop_rate has to be between 0 and 1")
        if n_units < 1:
            raise ValueError("Need at least one unit in each dense layer")
        if n_conv < 1:
            raise ValueError("Need at least one convolutional unit")
        self._n_units: int = n_units
        self._n_conv: int = n_conv
        self.input_length: int = input_length
        self._activation: str = activation
        self._drop_rate: float = drop_rate
        self.l2_sparsity: float = 2e-4  # sparsity constraint on weight vectors
        self.learning_rate: float = 1e-3
        # optimizer and loss functions
        self.optimizer: Optional[keras.optimizers.Optimizer] = None
        self.loss_fn: Optional[keras.losses.Loss] = None
        self._initialized: bool = False
        # output placeholders
        self._out: Optional[keras.layers.Layer] = None
        # layers
        self._conv_layer: Optional[keras.layers.Layer] = None  # Convolutional layer
        self._drop_cl: Optional[keras.layers.Layer] = None  # Dropout of convolutional layer
        self._deep_1: Optional[keras.layers.Layer] = None  # First deep layer
        self._drop_d1: Optional[keras.layers.Layer] = None  # Dropout of first deep layer
        self._deep_2: Optional[keras.layers.Layer] = None  # Second deep layer
        self._drop_d2: Optional[keras.layers.Layer] = None  # Dropout of second deep layer

        self._deep_3: Optional[keras.layers.Layer] = None  # Third deep layer
        self._drop_d3: Optional[keras.layers.Layer] = None  # Dropout of third deep layer
        self._deep_4: Optional[keras.layers.Layer] = None  # Fourth deep layer
        self._drop_d4: Optional[keras.layers.Layer] = None  # Dropout of fourth deep layer
        self._flatten: Optional[keras.layers.Layer] = None
        # model-specific cash field used during derivative calculation
        self.part_tensor_1: Optional[np.ndarray] = None
        # Store if this is a model to predict continuous data or spikes
        self.predict_spikes = predict_spikes

    def setup(self) -> None:
        """
        Initializes the model, resetting weights
        """
        # processing
        self._flatten = layers.Flatten()

        # Replace the Conv1D with a Dense layer.
        # Since kernel_size == input_length, this computes the exact same weights and math, but much faster.
        self._conv_layer = layers.Dense(units=self.n_conv,
                                        activation=self.activation,
                                        use_bias=True,
                                        kernel_initializer=initializers.GlorotUniform(),
                                        kernel_regularizer=regularizers.L2(self.l2_sparsity),
                                        name="PseudoConvolution")
        self._drop_cl = layers.Dropout(self.drop_rate)
        self._deep_1 = layers.Dense(units=self.n_units, activation=self.activation,
                                    kernel_initializer=initializers.GlorotUniform(),
                                    kernel_regularizer=regularizers.L2(self.l2_sparsity), name="Deep1")
        self._drop_d1 = layers.Dropout(self.drop_rate)
        self._deep_2 = layers.Dense(units=self.n_units, activation=self.activation,
                                    kernel_initializer=initializers.GlorotUniform(),
                                    kernel_regularizer=regularizers.L2(self.l2_sparsity), name="Deep2")
        self._drop_d2 = layers.Dropout(self.drop_rate)

        self._deep_3 = layers.Dense(units=self.n_units, activation=self.activation,
                                    kernel_initializer=initializers.GlorotUniform(),
                                    kernel_regularizer=regularizers.L2(self.l2_sparsity), name="Deep3")
        self._drop_d3 = layers.Dropout(self.drop_rate)
        self._deep_4 = layers.Dense(units=self.n_units, activation=self.activation,
                                    kernel_initializer=initializers.GlorotUniform(),
                                    kernel_regularizer=regularizers.L2(self.l2_sparsity), name="Deep4")
        self._drop_d4 = layers.Dropout(self.drop_rate)
        # output: This is just one value, that should predict the calcium response at the current time
        self._out = layers.Dense(1, activation=None, name="Out")

        # UPDATED: Replaced legacy Adam optimizer with standard Keras 3 Adam optimizer
        self.optimizer = keras.optimizers.Adam(learning_rate=self.learning_rate)

        # all we need to do to be able to predict spikes is change our loss function! This change is transparent
        if self.predict_spikes:
            self.loss_fn = keras.losses.BinaryCrossentropy(from_logits=True)
        else:
            self.loss_fn = keras.losses.MeanSquaredError()
        self._initialized = True

    def get_output(self, inputs: np.ndarray) -> np.ndarray:
        """
        Returns the output value given the model inputs
        """
        self.check_input(inputs)
        # Use the compiled graph instead of eager execution
        out = self.fast_predict(inputs)
        return out.numpy().ravel()

    def get_probability(self, inputs: np.ndarray) -> np.ndarray:
        """
        Returns the spike probability given model inputs
        """
        if not self.predict_spikes:
            raise ValueError("Model does not predict spikes. Probability representation is meaningless")
        self.check_input(inputs)

        # Use the compiled graph
        logit_out = self.fast_predict(inputs)
        return tf.math.sigmoid(logit_out).numpy().ravel()

    def clear_model(self) -> None:
        """
        Clears and uninitializes the model
        """
        self._conv_layer = None  # Convolutional layer
        self._drop_cl = None  # Dropout of convolutional layer
        self._deep_1 = None  # First deep layer
        self._drop_d1 = None  # Dropout of first deep layer
        self._deep_2 = None  # Second deep layer
        self._drop_d2 = None  # Dropout of second deep layer

        self._deep_3 = None  # Third deep layer
        self._drop_d3 = None  # Dropout of third deep layer
        self._deep_4 = None  # Fourth deep layer
        self._drop_d4 = None  # Dropout of fourth deep layer
        self._out = None
        self._initialized = False

    def check_init(self) -> None:
        if not self._initialized:
            raise NotInitialized("Model not initialized. Call setup or load.")

    def check_input(self, inputs) -> None:
        if inputs.shape[1] != self.input_length:
            raise ValueError("Input length across time different than expected")

    def call(self, inputs: Union[np.ndarray, tf.Tensor], training: Optional[bool] = None, mask=None) -> tf.Tensor:
        if training is None:
            training = False
        self.check_init()
        inputs = self._flatten(inputs)
        inputs = self._conv_layer(inputs, training=training)
        inputs = self._drop_cl(inputs, training=training)
        inputs = self._deep_1(inputs, training=training)
        inputs = self._drop_d1(inputs, training=training)
        inputs = self._deep_2(inputs, training=training)
        inputs = self._drop_d2(inputs, training=training)

        inputs = self._deep_3(inputs, training=training)
        inputs = self._drop_d3(inputs, training=training)
        inputs = self._deep_4(inputs, training=training)
        inputs = self._drop_d4(inputs, training=training)

        # Get the (BatchSize, 1) prediction from the final dense layer
        out = self._out(inputs)

        # 2. Squeeze the last axis to output (BatchSize,)
        # This perfectly aligns with your dataset labels and prevents Keras 3 shape broadcasting bugs
        return tf.squeeze(out, axis=-1)

    @tf.function(jit_compile=True)  # jit_compile=True enables XLA speedups for inference
    def fast_predict(self, inputs: tf.Tensor) -> tf.Tensor:
        """
        A compiled, highly optimized forward pass specifically for
        use outside the training loop.
        """
        # Call the base model with training=False to disable Dropout
        return self(inputs, training=False)

    @tf.function
    def perform_training_step(self, btch_inputs: tf.Tensor, btch_labels: tf.Tensor):
        with tf.GradientTape() as tape:
            pred = self(btch_inputs, training=True)

            loss = self.loss_fn(btch_labels, pred)
            # Handle Keras 3 regularization tracking safely
            if self.losses:
                loss += tf.math.add_n(self.losses)

        # Keras 3 standard property is trainable_weights
        trainable_vars = self.trainable_weights
        gradients = tape.gradient(loss, trainable_vars)
        self.optimizer.apply_gradients(zip(gradients, trainable_vars))
        return loss

    @property
    def activation(self) -> str:
        return self._activation

    @property
    def drop_rate(self) -> float:
        return self._drop_rate

    @property
    def n_units(self) -> int:
        return self._n_units

    @property
    def n_conv(self) -> int:
        return self._n_conv

    @property
    def conv_layer(self) -> Optional[keras.layers.Layer]:
        return self._conv_layer

    @property
    def deep_1(self) -> Optional[keras.layers.Layer]:
        return self._deep_1

    @property
    def deep_2(self) -> Optional[keras.layers.Layer]:
        return self._deep_2

    @property
    def deep_3(self) -> Optional[keras.layers.Layer]:
        return self._deep_3

    @property
    def deep_4(self) -> Optional[keras.layers.Layer]:
        return self._deep_4

    @property
    def flatten(self) -> Optional[keras.layers.Layer]:
        return self._flatten

    @property
    def out(self) -> Optional[keras.layers.Layer]:
        return self._out

def train_model(mdl: ActivityPredictor, tset: tf.data.Dataset, n_epochs: int, datacount: int) -> None:
    # Trigger weight initialization by fetching one batch and doing a dry run
    for dummy_inp, _ in tset.take(1):
        mdl(dummy_inp, training=False)

    # CRITICAL FIX: Build the Keras 3 optimizer variables before tracing the custom loop
    mdl.optimizer.build(mdl.trainable_variables)

    # Now execute the custom loop safely
    for e in range(n_epochs):
        for inp, outp in tset:
            mdl.perform_training_step(inp, outp)


def get_standard_model(hist_steps: int, predict_spikes: bool) -> ActivityPredictor:
    """
    Creates and returns an activity predictor instance with standard parameters
    found through a hyperparameter search
    :param hist_steps: The number of history steps in the model
    :param predict_spikes: If true, 0/1 spike data instead of continuous data is expected
    """
    m = ActivityPredictor(64, 80, 0.5, hist_steps, "swish", predict_spikes)
    m.learning_rate = 1e-3
    m.l2_sparsity = 1e-3
    m.setup()
    return m
