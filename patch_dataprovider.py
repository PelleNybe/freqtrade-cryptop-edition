import re

with open('freqtrade/data/dataprovider.py', 'r') as f:
    content = f.read()

# Add import
content = content.replace("from freqtrade.exchange import Exchange", "from freqtrade.exchange import Exchange\nfrom freqtrade.data.sentiment import NLPSentimentDaemon")

# Add init logic
init_patch = """        self.__rpc = rpc
        self._msg_queue: deque = deque()
        self._sentiment_daemon = NLPSentimentDaemon(self._config)
        if self._sentiment_daemon.enabled:
            self._sentiment_daemon.start()"""

content = content.replace("        self.__rpc = rpc\n        self._msg_queue: deque = deque()", init_patch)

# Add methods
methods_patch = '''

    def get_global_sentiment(self) -> float:
        """
        Get the current global market sentiment from the NLP Sentiment Daemon.
        Returns a float between -1.0 (bearish) and 1.0 (bullish).
        """
        if getattr(self, '_sentiment_daemon', None):
            return self._sentiment_daemon.get_global_sentiment()
        return 0.0

    def get_pair_sentiment(self, pair: str) -> float:
        """
        Get the current sentiment for a specific pair from the NLP Sentiment Daemon.
        Returns a float between -1.0 (bearish) and 1.0 (bullish).
        """
        if getattr(self, '_sentiment_daemon', None):
            return self._sentiment_daemon.get_pair_sentiment(pair)
        return 0.0
'''

content += methods_patch

with open('freqtrade/data/dataprovider.py', 'w') as f:
    f.write(content)
