import re

with open("freqtrade/rpc/rpc_manager.py", "r") as f:
    content = f.read()

apprise_patch = """        # EDGE OPTIMIZATION: Enable Prometheus
        if config.get("prometheus", {}).get("enabled", False):
            logger.info("Enabling rpc.prometheus ...")
            from freqtrade.rpc.prometheus import PrometheusExporter

            self.registered_modules.append(PrometheusExporter(freqtrade))

        # EDGE OPTIMIZATION: Enable Apprise Omni-Notifications
        if config.get("apprise", {}).get("enabled", False):
            logger.info("Enabling rpc.apprise ...")
            from freqtrade.rpc.apprise_notification import AppriseNotification

            self.registered_modules.append(AppriseNotification(freqtrade))"""

content = re.sub(
    r'        # EDGE OPTIMIZATION: Enable Prometheus\n        if config\.get\("prometheus", \{\}\)\.get\("enabled", False\):\n            logger\.info\("Enabling rpc\.prometheus \.\.\."\)\n            from freqtrade\.rpc\.prometheus import PrometheusExporter\n\n            self\.registered_modules\.append\(PrometheusExporter\(freqtrade\)\)',
    apprise_patch,
    content
)

with open("freqtrade/rpc/rpc_manager.py", "w") as f:
    f.write(content)
