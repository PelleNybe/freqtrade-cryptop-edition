import re

with open("freqtrade/rpc/rpc_manager.py", "r") as f:
    content = f.read()

prom_patch = """        # EDGE OPTIMIZATION: Enable MQTT
        if config.get("mqtt", {}).get("enabled", False):
            logger.info("Enabling rpc.mqtt ...")
            from freqtrade.rpc.mqtt import MQTT

            self.registered_modules.append(MQTT(freqtrade))

        # EDGE OPTIMIZATION: Enable Prometheus
        if config.get("prometheus", {}).get("enabled", False):
            logger.info("Enabling rpc.prometheus ...")
            from freqtrade.rpc.prometheus import PrometheusExporter

            self.registered_modules.append(PrometheusExporter(freqtrade))"""

content = re.sub(
    r'        # EDGE OPTIMIZATION: Enable MQTT\n        if config\.get\("mqtt", \{\}\)\.get\("enabled", False\):\n            logger\.info\("Enabling rpc\.mqtt \.\.\."\)\n            from freqtrade\.rpc\.mqtt import MQTT\n\n            self\.registered_modules\.append\(MQTT\(freqtrade\)\)',
    prom_patch,
    content
)

with open("freqtrade/rpc/rpc_manager.py", "w") as f:
    f.write(content)
