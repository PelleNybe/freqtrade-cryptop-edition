with open("freqtrade/rpc/api_server/webserver.py") as f:
    content = f.read()

# Add contextlib for lifespan
if "from contextlib import asynccontextmanager" not in content:
    content = content.replace(
        "from typing import Any",
        "from typing import Any\nfrom contextlib import asynccontextmanager",
    )

lifespan_logic = """
        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            self._api_startup_event()
            yield
            # Shutdown
            self._api_shutdown_event()

        self.app = FastAPI(
            lifespan=lifespan,
"""
content = content.replace("        self.app = FastAPI(", lifespan_logic)

content = content.replace(
    '        app.add_event_handler(event_type="startup", func=self._api_startup_event)', ""
)
content = content.replace(
    '        app.add_event_handler(event_type="shutdown", func=self._api_shutdown_event)', ""
)

with open("freqtrade/rpc/api_server/webserver.py", "w") as f:
    f.write(content)
