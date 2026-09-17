with open('freqtrade/exchange/exchange.py', 'r') as f:
    lines = f.readlines()

new_lines = []
imports = []
for line in lines:
    if line.startswith('import threading'):
        imports.append(line)
    elif line.startswith('import time') and 'exchange' in line:
        imports.append(line)
    else:
        new_lines.append(line)

final_lines = []
in_docstring = False
for i, line in enumerate(new_lines):
    if line.startswith('"""') and not in_docstring:
        in_docstring = True
        final_lines.append(line)
    elif line.startswith('"""') and in_docstring:
        in_docstring = False
        final_lines.append(line)
        # insert here
        final_lines.extend(imports)
    else:
        final_lines.append(line)

with open('freqtrade/exchange/exchange.py', 'w') as f:
    f.writelines(final_lines)
