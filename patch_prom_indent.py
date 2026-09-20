with open("freqtrade/rpc/prometheus.py", "r") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if line.startswith("    def send_msg(self, msg: RPCSendMsg) -> None:"):
        lines[i] = "    def send_msg(self, msg: RPCSendMsg) -> None:\n        pass\n"

with open("freqtrade/rpc/prometheus.py", "w") as f:
    f.writelines(lines)
