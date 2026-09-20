import time
from collections import deque
from unittest.mock import mock_open, patch

from freqtrade.freqai.freqai_interface import IFreqaiModel


class DummyFreqAI(IFreqaiModel):
    def __init__(self, **kwargs):
        # minimal mock init
        self.freqai_info = {"activate_tensorboard": False}
        self.config = {"timeframe": "5m", "exchange": {"pair_whitelist": []}}
        self.ft_params = {}
        self._thermal_history = deque(maxlen=30)

    def train(self):
        pass

    def predict(self):
        pass

    def fit(self):
        pass


@patch("freqtrade.freqai.freqai_interface.IFreqaiModel.__init__")
def test_thermal_throttle_reactive(mock_init):
    # test that we sleep 15s if temp > 75
    model = DummyFreqAI()
    model._thermal_history = deque(maxlen=30)

    mock_file = mock_open(read_data="76000\n")
    with patch("pathlib.Path.open", mock_file):
        with patch("time.sleep") as mock_sleep:
            model._check_thermal_throttle()
            mock_sleep.assert_called_once_with(15)
            assert len(model._thermal_history) == 0


@patch("freqtrade.freqai.freqai_interface.IFreqaiModel.__init__")
def test_thermal_throttle_predictive(mock_init):
    model = DummyFreqAI()
    model._thermal_history = deque(maxlen=30)

    base_time = time.time()
    # build a history that climbs fast: 60C, 62C, 64C, 66C, 68C, 70C
    # delta 2 degrees per 10 seconds (0.2C / sec)
    for i in range(6):
        model._thermal_history.append((base_time + i * 10, 60.0 + i * 2.0))

    # next read is 72C
    mock_file = mock_open(read_data="72000\n")
    with patch("time.time", return_value=base_time + 60):
        with patch("pathlib.Path.open", mock_file):
            with patch("time.sleep") as mock_sleep:
                model._check_thermal_throttle()
                # 0.2C/s * 300 = 60C + 72C = 132C > 75C, so should sleep 10s
                mock_sleep.assert_called_once_with(10)
                assert len(model._thermal_history) == 0


@patch("freqtrade.freqai.freqai_interface.IFreqaiModel.__init__")
def test_thermal_throttle_safe(mock_init):
    model = DummyFreqAI()
    model._thermal_history = deque(maxlen=30)

    base_time = time.time()
    # build a history that is flat: 40C, 40C...
    for i in range(6):
        model._thermal_history.append((base_time + i * 10, 40.0))

    mock_file = mock_open(read_data="40000\n")
    with patch("time.time", return_value=base_time + 60):
        with patch("pathlib.Path.open", mock_file):
            with patch("time.sleep") as mock_sleep:
                model._check_thermal_throttle()
                mock_sleep.assert_not_called()
                assert len(model._thermal_history) == 7
