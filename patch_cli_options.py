import re

with open("freqtrade/commands/cli_options.py", "r") as f:
    content = f.read()

resume_arg = """    "hyperopt_resume": Arg(
        "--resume",
        help="Resume Hyperopt from the last saved checkpoint on NVMe.",
        action="store_true",
        default=False,
    ),
    "hyperopt_jobs": Arg("""

content = re.sub(r'    "hyperopt_jobs": Arg\(', resume_arg, content)

with open("freqtrade/commands/cli_options.py", "w") as f:
    f.write(content)
