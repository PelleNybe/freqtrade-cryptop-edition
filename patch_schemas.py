import re


with open("freqtrade/rpc/api_server/api_schemas.py") as f:
    content = f.read()

replacement = """class SysInfo(BaseModel):
    cpu_pct: list[float]
    ram_pct: float
    cpu_temp: float | None = None
    disk_read_bytes: int | None = None
    disk_write_bytes: int | None = None
    uptime_seconds: int | None = None
    python_version: str | None = None
    freqtrade_version: str | None = None"""

content = re.sub(
    r"class SysInfo\(BaseModel\):.*?disk_write_bytes: int \| None = None",
    replacement,
    content,
    flags=re.DOTALL,
)

with open("freqtrade/rpc/api_server/api_schemas.py", "w") as f:
    f.write(content)
