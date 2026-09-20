import base64
import json
import logging
import threading
from typing import Any

import numpy as np
import torch


logger = logging.getLogger(__name__)


class FederatedAveragingDaemon:
    """
    Background daemon for FreqAI Federated Learning (Swarm Mode).
    Listens to MQTT for peer model weights, stores them, and applies FedAvg
    before the next inference/training cycle.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.mqtt_config = config.get("mqtt", {})
        self.enabled = config.get("freqai", {}).get("federated_learning", False)
        self.peer_weights: dict[str, dict[str, torch.Tensor]] = {}
        self.lock = threading.Lock()
        self.client = None
        self.topic = self.mqtt_config.get("topic", "freqtrade") + "/federated/weights"

        if self.enabled:
            self._start_mqtt()

    def _start_mqtt(self):
        try:
            import paho.mqtt.client as mqtt

            self.client = mqtt.Client(client_id="freqai_federated_" + str(id(self)))

            if "username" in self.mqtt_config and "password" in self.mqtt_config:
                self.client.username_pw_set(
                    self.mqtt_config["username"], self.mqtt_config["password"]
                )

            self.client.on_connect = self._on_connect
            self.client.on_message = self._on_message

            host = self.mqtt_config.get("host", "127.0.0.1")
            port = self.mqtt_config.get("port", 1883)

            self.client.connect_async(host, port, 60)
            self.client.loop_start()
            logger.info(f"FederatedAveragingDaemon connected to MQTT broker at {host}:{port}")
        except ImportError:
            logger.error(
                "paho-mqtt missing. Run `pip install paho-mqtt` to use Federated Learning."
            )
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Federated MQTT client: {e}")
            self.enabled = False

    def _on_connect(self, client, userdata, flags, rc):
        logger.info(f"Federated MQTT connected with result code {rc}. Subscribing to {self.topic}")
        client.subscribe(self.topic)

    def _on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode())
            node_id = payload.get("node_id")
            if not node_id:
                return

            weights_b64 = payload.get("weights")
            if not weights_b64:
                return

            state_dict = self.deserialize_weights(weights_b64)
            with self.lock:
                self.peer_weights[node_id] = state_dict
                logger.info(f"Received federated weights from peer: {node_id}")
        except Exception as e:
            logger.warning(f"Failed to parse federated weights payload: {e}")

    def apply_fedavg(self, local_model: torch.nn.Module) -> None:
        """
        Applies Federated Averaging (FedAvg) to the local PyTorch model.
        """
        if not self.enabled:
            return

        with self.lock:
            if not self.peer_weights:
                logger.debug("No peer weights available for FedAvg.")
                return

            logger.info(f"Applying FedAvg with {len(self.peer_weights)} peer models.")
            local_state_dict = local_model.state_dict()

            # FedAvg: weight_new = (local_weight + sum(peer_weights)) / (1 + num_peers)

            for key in local_state_dict.keys():
                # Make sure the peer has this key and matching shape
                valid_peer_tensors = []
                for peer_id, peer_state in self.peer_weights.items():
                    if key in peer_state and peer_state[key].shape == local_state_dict[key].shape:
                        valid_peer_tensors.append(peer_state[key].to(local_state_dict[key].device))

                if not valid_peer_tensors:
                    continue

                sum_peer_tensor = torch.stack(valid_peer_tensors).sum(dim=0)
                averaged_tensor = (local_state_dict[key] + sum_peer_tensor) / (
                    1 + len(valid_peer_tensors)
                )
                local_state_dict[key].copy_(averaged_tensor)

            # Clear peer weights after applying
            self.peer_weights.clear()

    def publish_weights(self, local_model: torch.nn.Module, node_id: str) -> None:
        """
        Serializes and publishes local model weights to the MQTT swarm.
        """
        if not self.enabled or not self.client:
            return

        try:
            weights_b64 = self.serialize_weights(local_model.state_dict())
            payload = {"node_id": node_id, "weights": weights_b64}
            self.client.publish(self.topic, json.dumps(payload))
            logger.info("Published local weights to federated swarm.")
        except Exception as e:
            logger.warning(f"Failed to publish federated weights: {e}")

    @staticmethod
    def serialize_weights(state_dict: dict[str, torch.Tensor]) -> str:
        """
        Serializes PyTorch state_dict to a base64 encoded JSON string.
        (Uses float16 quantization for bandwidth savings).
        """
        numpy_dict = {}
        for k, v in state_dict.items():
            # Convert to float16 to save bandwidth on edge networks
            numpy_dict[k] = v.cpu().numpy().astype(np.float16).tolist()

        json_str = json.dumps(numpy_dict)
        return base64.b64encode(json_str.encode("utf-8")).decode("utf-8")

    @staticmethod
    def deserialize_weights(b64_str: str) -> dict[str, torch.Tensor]:
        """
        Deserializes a base64 encoded JSON string back into a PyTorch state_dict.
        """
        json_str = base64.b64decode(b64_str.encode("utf-8")).decode("utf-8")
        numpy_dict = json.loads(json_str)

        state_dict = {}
        for k, v in numpy_dict.items():
            state_dict[k] = torch.tensor(np.array(v, dtype=np.float32))
        return state_dict

    def cleanup(self):
        if self.enabled and self.client:
            self.client.loop_stop()
            self.client.disconnect()
