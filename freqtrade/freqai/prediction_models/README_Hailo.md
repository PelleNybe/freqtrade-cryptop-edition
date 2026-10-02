# Hailo AI Integration in FreqAI

Implementing a Hailo AI model in FreqAI on a Raspberry Pi 5 requires an understanding of edge ML deployment.
Because the Hailo AI hat uses a specialized TPU, you cannot *train* (compile) the model directly on the Raspberry Pi.

Here is the high-level workflow:

1. **Train your model on a Host PC (x86)**: Train your PyTorch/TensorFlow model on your powerful desktop/cloud machine using standard FreqAI tools (e.g., PyTorchRegressor).
2. **Compile the model for Hailo**: Use the [Hailo Dataflow Compiler](https://hailo.ai/developer-zone/software-downloads/) on your Host PC to convert your trained `.onnx` or `.pb` model into a Hailo Executable Format (`.hef`) file.
3. **Deploy to Raspberry Pi 5**: Move the `.hef` file to your Raspberry Pi 5.
4. **Run Inference with Custom FreqAI Model**: Use the `HailoRegressor` custom model script to run live predictions.

## Installation on Raspberry Pi 5

You must install the HailoRT (Hailo Runtime) and its Python bindings on your Raspberry Pi:

```bash
sudo apt install hailo-all
# Make sure to install the python bindings into the same virtual environment Freqtrade uses.
```

## Configuring Freqtrade

In your `config.json`, tell FreqAI to use the `HailoRegressor` and point it to your compiled `.hef` file.
Importantly, you must disable live retraining since you cannot compile `.hef` files on the Pi.

```json
{
    "freqai": {
        "enabled": true,
        "purge_old_models": 2,
        "train_period_days": 0,
        "live_retrain_hours": 0,
        "identifier": "hailo_experiment",
        "feature_parameters": {
            "include_timeframes": ["5m", "15m"],
            "include_corr_pairlist": ["BTC/USDT", "ETH/USDT"]
        },
        "model_training_parameters": {
            "hef_path": "user_data/models/my_hailo_model.hef"
        }
    }
}
```

Then run your bot:
```bash
freqtrade trade --config config.json --strategy MyStrategy --freqaimodel HailoRegressor
```
