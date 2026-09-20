import re

with open('freqtrade/data/dataprovider.py', 'r') as f:
    content = f.read()

content = content.replace("from freqtrade.data.sentiment import NLPSentimentDaemon, timeframe_to_prev_date, timeframe_to_seconds", "from freqtrade.data.sentiment import NLPSentimentDaemon\nfrom freqtrade.exchange import timeframe_to_prev_date, timeframe_to_seconds")

with open('freqtrade/data/dataprovider.py', 'w') as f:
    f.write(content)
