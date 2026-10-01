import re


with open("freqtrade/rpc/rpc.py") as f:
    content = f.read()

replacement = """        except Exception:
            disk_read = 0
            disk_write = 0

        import platform
        from freqtrade import __version__
        uptime = 0
        try:
            uptime = int(time.time() - psutil.boot_time())
        except Exception:
            pass

        return {
            "cpu_pct": psutil.cpu_percent(interval=1, percpu=True),
            "ram_pct": psutil.virtual_memory().percent,
            "cpu_temp": temp,
            "disk_read_bytes": disk_read,
            "disk_write_bytes": disk_write,
            "uptime_seconds": uptime,
            "python_version": platform.python_version(),
            "freqtrade_version": __version__,
        }"""

content = re.sub(
    r'        except Exception:\n            disk_read = 0\n            disk_write = 0\n\n        return {\n            "cpu_pct": psutil.cpu_percent\(interval=1, percpu=True\),\n            "ram_pct": psutil.virtual_memory\(\).percent,\n            "cpu_temp": temp,\n            "disk_read_bytes": disk_read,\n            "disk_write_bytes": disk_write,\n        }',
    replacement,
    content,
    flags=re.DOTALL,
)

with open("freqtrade/rpc/rpc.py", "w") as f:
    f.write(content)
