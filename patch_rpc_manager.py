import re

with open("freqtrade/rpc/rpc_manager.py", "r") as f:
    content = f.read()

mqtt_patch = """        # Enable Webhook
        if config.get("webhook", {}).get("enabled", False):
            logger.info("Enabling rpc.webhook ...")
            from freqtrade.rpc.webhook import Webhook

            self.registered_modules.append(Webhook(self._rpc, config))

        # EDGE OPTIMIZATION: Enable MQTT
        if config.get("mqtt", {}).get("enabled", False):
            logger.info("Enabling rpc.mqtt ...")
            from freqtrade.rpc.mqtt import MQTT

            self.registered_modules.append(MQTT(freqtrade))"""

content = re.sub(
    r'        # Enable Webhook\n        if config\.get\("webhook", \{\}\)\.get\("enabled", False\):\n            logger\.info\("Enabling rpc\.webhook \.\.\."\)\n            from freqtrade\.rpc\.webhook import Webhook\n\n            self\.registered_modules\.append\(Webhook\(self\._rpc, config\)\)',
    mqtt_patch,
    content
)

with open("freqtrade/rpc/rpc_manager.py", "w") as f:
    f.write(content)
