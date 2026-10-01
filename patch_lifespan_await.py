with open("freqtrade/rpc/api_server/webserver.py") as f:
    content = f.read()

content = content.replace(
    "            self._api_startup_event()", "            await self._api_startup_event()"
)
content = content.replace(
    "            self._api_shutdown_event()", "            await self._api_shutdown_event()"
)

with open("freqtrade/rpc/api_server/webserver.py", "w") as f:
    f.write(content)
