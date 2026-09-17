import re

with open("freqtrade/rpc/rpc.py", "r") as f:
    content = f.read()

new_sysinfo = """    @staticmethod
    def _rpc_sysinfo() -> dict[str, Any]:
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = float(f.read()) / 1000.0
        except Exception:
            temp = 0.0

        try:
            disk_io = psutil.disk_io_counters()
            disk_read = disk_io.read_bytes
            disk_write = disk_io.write_bytes
        except Exception:
            disk_read = 0
            disk_write = 0

        return {
            "cpu_pct": psutil.cpu_percent(interval=1, percpu=True),
            "ram_pct": psutil.virtual_memory().percent,
            "cpu_temp": temp,
            "disk_read_bytes": disk_read,
            "disk_write_bytes": disk_write,
        }"""

content = re.sub(r'    @staticmethod\n    def _rpc_sysinfo\(\) -> dict\[str, Any\]:\n        return \{\n            "cpu_pct": psutil\.cpu_percent\(interval=1, percpu=True\),\n            "ram_pct": psutil\.virtual_memory\(\)\.percent,\n        \}', new_sysinfo, content)

with open("freqtrade/rpc/rpc.py", "w") as f:
    f.write(content)
