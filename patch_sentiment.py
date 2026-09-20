import re

with open('freqtrade/data/sentiment.py', 'r') as f:
    content = f.read()

# Fix long lines
content = content.replace('"llama-cpp-python missing. Run `pip install llama-cpp-python` to use NLP Sentiment Daemon."', '("llama-cpp-python missing. Run `pip install llama-cpp-python` "\n                "to use NLP Sentiment Daemon.")')
content = content.replace('prompt = f"Analyze the sentiment of the following crypto news headline and respond with ONLY a single float number between -1.0 (extremely bearish) and 1.0 (extremely bullish). Headline: \'{news}\'"', 'prompt = (f"Analyze the sentiment of the following crypto news headline and "\n                      f"respond with ONLY a single float number between -1.0 (extremely bearish) "\n                      f"and 1.0 (extremely bullish). Headline: \'{news}\'")')

# Ignore sec warnings
content = content.replace("with urllib.request.urlopen(req, timeout=10) as response:", "with urllib.request.urlopen(req, timeout=10) as response: # noqa: S310")
content = content.replace("req = urllib.request.Request(feed_url, headers={\"User-Agent\": \"Mozilla/5.0\"})", "req = urllib.request.Request(feed_url, headers={\"User-Agent\": \"Mozilla/5.0\"}) # noqa: S310")
content = content.replace("root = ET.fromstring(xml_data)", "root = ET.fromstring(xml_data) # noqa: S314")

with open('freqtrade/data/sentiment.py', 'w') as f:
    f.write(content)
