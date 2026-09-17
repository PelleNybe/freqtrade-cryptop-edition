import re

with open("freqtrade/rpc/api_server/api_schemas.py", "r") as f:
    content = f.read()

new_schema = """class SysInfo(BaseModel):
    cpu_pct: list[float]
    ram_pct: float
    cpu_temp: float | None = None
    disk_read_bytes: int | None = None
    disk_write_bytes: int | None = None"""

content = re.sub(r'class SysInfo\(BaseModel\):\n    cpu_pct: list\[float\]\n    ram_pct: float', new_schema, content)

with open("freqtrade/rpc/api_server/api_schemas.py", "w") as f:
    f.write(content)
