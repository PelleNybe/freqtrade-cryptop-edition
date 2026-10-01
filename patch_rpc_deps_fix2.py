with open("freqtrade/rpc/rpc.py") as f:
    content = f.read()

content = content.replace(
    """        except Exception:
            pass""",
    """        except Exception as e:
            logger.debug(f"Failed to get uptime: {e}")""",
)

with open("freqtrade/rpc/rpc.py", "w") as f:
    f.write(content)
