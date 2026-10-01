with open("freqtrade/rpc/rpc.py") as f:
    content = f.read()

content = content.replace(
    "uptime = int(time.time() - psutil.boot_time())",
    "import time\n            uptime = int(time.time() - psutil.boot_time())",
)

with open("freqtrade/rpc/rpc.py", "w") as f:
    f.write(content)

with open("freqtrade/rpc/api_server/deps.py") as f:
    content = f.read()

# Fix E402 and F811 by removing the redundant imports at the bottom
content = content.replace("import functools\nfrom cachetools import TTLCache", "")

with open("freqtrade/rpc/api_server/deps.py", "w") as f:
    f.write(content)

# We need to add `import functools` to the top of deps.py
with open("freqtrade/rpc/api_server/deps.py") as f:
    content = f.read()

content = "import functools\n" + content
with open("freqtrade/rpc/api_server/deps.py", "w") as f:
    f.write(content)

with open("freqtrade/rpc/api_server/api_v1.py") as f:
    content = f.read()

content = content.replace("except Exception as e:", "except Exception:")

with open("freqtrade/rpc/api_server/api_v1.py", "w") as f:
    f.write(content)
