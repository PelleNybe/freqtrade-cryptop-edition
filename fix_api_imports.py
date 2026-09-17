with open('freqtrade/rpc/api_server/api_trading.py', 'r') as f:
    lines = f.readlines()

new_lines = []
imports = []
for line in lines:
    if line.startswith('from cachetools import cached, TTLCache'):
        imports.append(line)
    else:
        new_lines.append(line)

new_content = ''.join(new_lines)

with open('freqtrade/rpc/api_server/api_trading.py', 'w') as f:
    f.write('from cachetools import cached, TTLCache\n')
    f.write(new_content)
