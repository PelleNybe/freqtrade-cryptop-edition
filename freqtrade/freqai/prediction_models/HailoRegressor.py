import logging
from pathlib import Path
from typing import Any

import numpy as np
import numpy.typing as npt
from pandas import DataFrame

from freqtrade.freqai.base_models.BaseRegressionModel import BaseRegressionModel
from freqtrade.freqai.data_kitchen import FreqaiDataKitchen


logger = logging.getLogger(__name__)

# Note: HailoRT bindings are required. Ensure `hailo` and `hailo_platform` are installed.
# https://github.com/hailo-ai/hailort
try:
    from hailo_platform import (
        HEF,
        ConfigureParams,
        HailoStreamInterface,
        VDevice,
    )
except ImportError:
    logger.warning("HailoRT is not installed or accessible. Inference will fail.")


class HailoRegressor(BaseRegressionModel):
    """
    Custom prediction model for Hailo AI accelerator on Raspberry Pi 5.

    This model assumes you have already trained a model (e.g., PyTorch, TensorFlow)
    and compiled it to a `.hef` file using the Hailo Dataflow Compiler on an x86 machine.

    The FreqAI configuration should disable continuous training by setting:
    "fit_live_predictions_candles": 0, or by using "train_period_days" properly,
    or supplying a pre-trained model directory.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hef_path = self.freqai_info.get("model_training_parameters", {}).get(
            "hef_path", "user_data/models/my_hailo_model.hef"
        )
        self.target = self.freqai_info.get("model_training_parameters", {}).get("target", "hailo8")
        self._vdevice = None
        self._infer_model = None
        self._configured_network = None

        # We lazily initialize HailoRT in predict or fit (if dummy)

    def _init_hailo(self):
        if self._vdevice is not None:
            return

        if not Path(self.hef_path).exists():
            raise FileNotFoundError(
                f"Hailo HEF model not found at {self.hef_path}. "
                f"Please compile your model and place it there."
            )

        logger.info(f"Loading Hailo HEF model from {self.hef_path}")
        self.hef = HEF(self.hef_path)

        # Configure VDevice (Virtual Device)
        params = VDevice.create_params()
        self._vdevice = VDevice(params)

        # Configure Network Group
        configure_params = ConfigureParams.create_from_hef(
            hef=self.hef, interface=HailoStreamInterface.PCIe
        )
        network_groups = self._vdevice.configure(self.hef, configure_params)
        self._network_group = network_groups[0]
        self._network_group_params = self._network_group.create_params()

        # Get input and output stream information
        self._input_vstream_info = self.hef.get_input_vstream_infos()[0]
        self._output_vstream_info = self.hef.get_output_vstream_infos()[0]

    def fit(self, data_dictionary: dict, dk: FreqaiDataKitchen, **kwargs) -> Any:
        """
        Since Hailo compilation takes place on an x86 host using the Dataflow Compiler,
        we do not actually train the model here on the Raspberry Pi.

        We can either return a dummy model or initialize the Hailo device.
        """
        logger.info("Hailo models are pre-trained. Skipping live training.")

        # Return something to indicate fit is 'done'. The object itself represents the model.
        return "hailo_dummy_model_wrapper"

    def predict(
        self, unfiltered_df: DataFrame, dk: FreqaiDataKitchen, **kwargs
    ) -> tuple[DataFrame, npt.NDArray[np.int_]]:
        """
        Filter the prediction features data and predict with it using Hailo.
        """
        self._init_hailo()

        dk.find_features(unfiltered_df)
        dk.data_dictionary["prediction_features"], _ = dk.filter_features(
            unfiltered_df, dk.training_features_list, training_filter=False
        )

        dk.data_dictionary["prediction_features"], outliers, _ = dk.feature_pipeline.transform(
            dk.data_dictionary["prediction_features"], outlier_check=True
        )

        # Prepare data for Hailo
        # Hailo models typically expect a specific shape e.g., (batch_size, channels, H, W)
        # or (batch_size, features). You must reshape based on what your HEF expects.
        X = dk.data_dictionary["prediction_features"].to_numpy().astype(np.float32)

        # Example: Reshape if your model expects (Batch, 1, 1, Features)
        # X = np.expand_dims(X, axis=(1, 2))

        # Infer using HailoRT
        predictions = []

        from hailo_platform import InferVStreams

        with InferVStreams(
            self._network_group, self._input_vstream_info, self._output_vstream_info
        ) as infer_pipeline:
            # For simplicity, sending the whole batch.
            # In production, consider batching if X is very large
            input_data = {self._input_vstream_info.name: X}
            with self._network_group.activate(self._network_group_params):
                infer_results = infer_pipeline.infer(input_data)

            out = infer_results[self._output_vstream_info.name]
            predictions = out

        predictions = np.array(predictions)

        if self.CONV_WIDTH == 1:
            predictions = np.reshape(predictions, (-1, len(dk.label_list)))

        pred_df = DataFrame(predictions, columns=dk.label_list)

        pred_df, _, _ = dk.label_pipeline.inverse_transform(pred_df)
        if dk.feature_pipeline["di"]:
            dk.DI_values = dk.feature_pipeline["di"].di_values
        else:
            dk.DI_values = np.zeros(outliers.shape[0])
        dk.do_predict = outliers

        return (pred_df, dk.do_predict)
