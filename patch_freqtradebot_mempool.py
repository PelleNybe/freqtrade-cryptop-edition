import re

with open('freqtrade/freqtradebot.py', 'r') as f:
    content = f.read()

cleanup_patch = """        # Stop Sentiment Daemon
        if hasattr(self, 'dataprovider') and hasattr(self.dataprovider, '_sentiment_daemon'):
            self.dataprovider._sentiment_daemon.stop()
            self.dataprovider._sentiment_daemon.join(timeout=2.0)

        # Stop Mempool Daemon
        if hasattr(self, 'dataprovider') and hasattr(self.dataprovider, '_mempool_daemon'):
            self.dataprovider._mempool_daemon.stop()
            self.dataprovider._mempool_daemon.join(timeout=2.0)"""

content = content.replace("""        # Stop Sentiment Daemon
        if hasattr(self, 'dataprovider') and hasattr(self.dataprovider, '_sentiment_daemon'):
            self.dataprovider._sentiment_daemon.stop()
            self.dataprovider._sentiment_daemon.join(timeout=2.0)""", cleanup_patch)

with open('freqtrade/freqtradebot.py', 'w') as f:
    f.write(content)
