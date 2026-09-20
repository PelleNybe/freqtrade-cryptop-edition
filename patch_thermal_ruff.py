import re

with open('freqtrade/freqai/freqai_interface.py', 'r') as f:
    content = f.read()

content = content.replace('f"[PREDICTIVE THROTTLE] CPU at {current_temp:.1f}C, but predicted to hit "', 'f"[PREDICTIVE THROTTLE] CPU at {current_temp:.1f}C, but predicted "\n                                f"to hit "')

with open('freqtrade/freqai/freqai_interface.py', 'w') as f:
    f.write(content)
