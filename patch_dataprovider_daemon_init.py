import re

with open('freqtrade/data/dataprovider.py', 'r') as f:
    content = f.read()

init_patch = """
        self.producers = self._config.get("external_message_consumer", {}).get("producers", [])
        self.external_data_enabled = len(self.producers) > 0

        self._sentiment_daemon = NLPSentimentDaemon(self._config)
        if self._sentiment_daemon.enabled:
            self._sentiment_daemon.start()"""

content = content.replace('        self.producers = self._config.get("external_message_consumer", {}).get("producers", [])\n        self.external_data_enabled = len(self.producers) > 0', init_patch)

with open('freqtrade/data/dataprovider.py', 'w') as f:
    f.write(content)
