import re

with open('freqtrade/data/dataprovider.py', 'r') as f:
    content = f.read()

content = content.replace("from freqtrade.data.sentiment import SentimentProvider", "from freqtrade.data.sentiment import NLPSentimentDaemon")

with open('freqtrade/data/dataprovider.py', 'w') as f:
    f.write(content)
