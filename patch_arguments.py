import re

with open("freqtrade/commands/arguments.py", "r") as f:
    content = f.read()

resume_arg = """    "export_csv",
    "hyperopt_resume","""

content = re.sub(r'    "export_csv",', resume_arg, content)

with open("freqtrade/commands/arguments.py", "w") as f:
    f.write(content)
