import re

with open('freqtrade/freqai/__init__.py', 'r') as f:
    content = f.read()

patch_code = "from freqtrade.freqai.federated_learning import FederatedAveragingDaemon\n\n__all__ = ['FederatedAveragingDaemon']"

with open('freqtrade/freqai/__init__.py', 'w') as f:
    f.write(content + "\n" + patch_code)
