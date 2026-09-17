with open('freqtrade/rpc/apprise_notification.py', 'r') as f:
    lines = f.readlines()

new_lines = []
imports = []
for line in lines:
    if line.startswith('import apprise'):
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

with open('freqtrade/rpc/apprise_notification.py', 'w') as f:
    f.writelines(final_lines)
