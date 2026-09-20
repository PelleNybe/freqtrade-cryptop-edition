import re

with open('freqtrade/data/dataprovider.py', 'r') as f:
    content = f.read()

import_patch = """from freqtrade.data.history import get_datahandler, load_pair_history
from freqtrade.data.mempool import MempoolDaemon
from freqtrade.data.sentiment import NLPSentimentDaemon"""

content = content.replace("from freqtrade.data.history import get_datahandler, load_pair_history\nfrom freqtrade.data.sentiment import NLPSentimentDaemon", import_patch)

init_patch = """        self._sentiment_daemon = NLPSentimentDaemon(self._config)
        if self._sentiment_daemon.enabled:
            self._sentiment_daemon.start()

        self._mempool_daemon = MempoolDaemon(self._config)
        if self._mempool_daemon.enabled:
            self._mempool_daemon.start()"""

content = content.replace("""        self._sentiment_daemon = NLPSentimentDaemon(self._config)
        if self._sentiment_daemon.enabled:
            self._sentiment_daemon.start()""", init_patch)

methods_patch = """

    def get_mempool_activity(self) -> float:
        \"\"\"
        Get the current normalized mempool activity score (0.0 to 1.0).
        \"\"\"
        if getattr(self, '_mempool_daemon', None):
            return self._mempool_daemon.get_mempool_activity()
        return 0.0
"""

content += methods_patch

with open('freqtrade/data/dataprovider.py', 'w') as f:
    f.write(content)
