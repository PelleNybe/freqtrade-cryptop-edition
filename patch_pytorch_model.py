import re

with open('freqtrade/freqai/base_models/BasePyTorchModel.py', 'r') as f:
    content = f.read()

# Add initialization of FederatedAveragingDaemon in __init__
init_patch = """        self.window_size = self.freqai_info.get("conv_width", 1)

        # Initialize Federated Learning Swarm Daemon
        self.federated_daemon = FederatedAveragingDaemon(self.config)
        self.node_id = self.config.get("bot_name", "freqai_node_" + str(id(self)))
"""

content = content.replace('        self.window_size = self.freqai_info.get("conv_width", 1)', init_patch)

with open('freqtrade/freqai/base_models/BasePyTorchModel.py', 'w') as f:
    f.write(content)
