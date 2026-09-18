import re

with open('freqtrade/freqai/base_models/BasePyTorchRegressor.py', 'r') as f:
    content = f.read()

patch_code = """        model = self.fit(dd, dk)

        # Apply federated averaging and publish weights
        if getattr(self, "federated_daemon", None) and self.federated_daemon.enabled and hasattr(model, "model"):
            self.federated_daemon.apply_fedavg(model.model)
            self.federated_daemon.publish_weights(model.model, getattr(self, "node_id", "node"))

        end_time = time()"""

content = content.replace("""        model = self.fit(dd, dk)

        # Apply federated averaging and publish weights
        if self.federated_daemon.enabled and hasattr(model, "model"):
            self.federated_daemon.apply_fedavg(model.model)
            self.federated_daemon.publish_weights(model.model, self.node_id)

        end_time = time()""", patch_code)

with open('freqtrade/freqai/base_models/BasePyTorchRegressor.py', 'w') as f:
    f.write(content)
