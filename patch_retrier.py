import re

with open("freqtrade/exchange/common.py", "r") as f:
    content = f.read()

# Enhance calculate_backoff for better edge network resilience
backoff_patch = """def calculate_backoff(retrycount, max_retries):
    \"\"\"
    Calculate backoff - EDGE OPTIMIZATION: Exponential backoff with jitter
    to handle poor 4G/LTE or spotty Wi-Fi networks more gracefully.
    \"\"\"
    import random
    base = 2 ** (max_retries - retrycount)
    jitter = random.uniform(0.5, 1.5)
    return max(1.0, min(base * jitter, 30.0))"""

content = re.sub(
    r'def calculate_backoff\(retrycount, max_retries\):\n    """\n    Calculate backoff\n    """\n    return \(max_retries - retrycount\) \*\* 2 \+ 1',
    backoff_patch,
    content
)

with open("freqtrade/exchange/common.py", "w") as f:
    f.write(content)
