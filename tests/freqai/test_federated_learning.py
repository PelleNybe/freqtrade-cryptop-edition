import pytest
import torch
import json
import base64
from unittest.mock import patch, MagicMock
from freqtrade.freqai.federated_learning import FederatedAveragingDaemon

class DummyModel(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.fc = torch.nn.Linear(2, 2)

def test_federated_daemon_disabled():
    config = {"freqai": {"federated_learning": False}}
    daemon = FederatedAveragingDaemon(config)
    assert not daemon.enabled

@patch("paho.mqtt.client.Client")
def test_federated_daemon_publish(mock_mqtt):
    config = {"freqai": {"federated_learning": True}, "mqtt": {"host": "test"}}
    daemon = FederatedAveragingDaemon(config)
    assert daemon.enabled

    model = DummyModel()
    daemon.publish_weights(model, "node_1")

    daemon.client.publish.assert_called_once()
    args, kwargs = daemon.client.publish.call_args
    assert args[0] == "freqtrade/federated/weights"
    payload = json.loads(args[1])
    assert payload["node_id"] == "node_1"
    assert "weights" in payload

@patch("paho.mqtt.client.Client")
def test_federated_daemon_receive_and_apply(mock_mqtt):
    config = {"freqai": {"federated_learning": True}}
    daemon = FederatedAveragingDaemon(config)

    local_model = DummyModel()
    peer_model_1 = DummyModel()

    # modify peer model weights so they are different
    with torch.no_grad():
        peer_model_1.fc.weight.fill_(1.0)
        local_model.fc.weight.fill_(0.0)

    weights_b64 = daemon.serialize_weights(peer_model_1.state_dict())

    # Simulate receiving message
    msg = MagicMock()
    msg.payload = json.dumps({"node_id": "node_2", "weights": weights_b64}).encode()

    daemon._on_message(None, None, msg)

    assert "node_2" in daemon.peer_weights

    # Apply FedAvg: (0 + 1) / 2 = 0.5
    daemon.apply_fedavg(local_model)

    assert torch.allclose(local_model.fc.weight, torch.tensor([[0.5, 0.5], [0.5, 0.5]]))
    assert len(daemon.peer_weights) == 0 # cleared after applying
