import re

with open('tests/freqai/test_thermal.py', 'r') as f:
    content = f.read()

patch_code = """class DummyFreqAI(IFreqaiModel):
    def __init__(self, **kwargs):
        # minimal mock init
        self.freqai_info = {"activate_tensorboard": False}
        self.config = {"timeframe": "5m", "exchange": {"pair_whitelist": []}}
        self.ft_params = {}
        self._thermal_history = deque(maxlen=30)
    def train(self): pass
    def predict(self): pass
    def fit(self): pass
"""

content = content.replace("""class DummyFreqAI(IFreqaiModel):
    def __init__(self, **kwargs):
        # minimal mock init
        self.freqai_info = {"activate_tensorboard": False}
        self.config = {"timeframe": "5m", "exchange": {"pair_whitelist": []}}
        self.ft_params = {}
        self._thermal_history = deque(maxlen=30)""", patch_code)

with open('tests/freqai/test_thermal.py', 'w') as f:
    f.write(content)
