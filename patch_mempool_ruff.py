import re

with open('freqtrade/data/mempool.py', 'r') as f:
    content = f.read()

content = content.replace("# For compatibility across varying nodes (Infura, local), polling 'pending' block is most stable.", "# For compatibility across nodes (Infura, local), polling 'pending' block is stable.")

with open('freqtrade/data/mempool.py', 'w') as f:
    f.write(content)
