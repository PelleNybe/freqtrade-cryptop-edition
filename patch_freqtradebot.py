import re

with open('freqtrade/freqtradebot.py', 'r') as f:
    content = f.read()

# Add logic to stop sentiment daemon if running inside dataprovider
patch_code = """        logger.info("Cleaning up modules ...")

        # Stop Sentiment Daemon
        if hasattr(self, 'dataprovider') and hasattr(self.dataprovider, '_sentiment_daemon'):
            self.dataprovider._sentiment_daemon.stop()
            self.dataprovider._sentiment_daemon.join(timeout=2.0)
"""

content = content.replace("        logger.info(\"Cleaning up modules ...\")", patch_code)

with open('freqtrade/freqtradebot.py', 'w') as f:
    f.write(content)
