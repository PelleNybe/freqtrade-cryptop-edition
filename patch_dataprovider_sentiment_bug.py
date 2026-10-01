with open("freqtrade/data/dataprovider.py") as f:
    content = f.read()

content = content.replace("self._sentiment = SentimentProvider(config)", "")

with open("freqtrade/data/dataprovider.py", "w") as f:
    f.write(content)
