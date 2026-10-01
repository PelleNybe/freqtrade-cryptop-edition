with open("freqtrade/rpc/api_server/webserver.py") as f:
    content = f.read()

# Revert lifespan
content = content.replace(
    """        @asynccontextmanager
        async def lifespan(app: FastAPI):
            # Startup
            await self._api_startup_event()
            yield
            # Shutdown
            await self._api_shutdown_event()

        self.app = FastAPI(
            lifespan=lifespan,""",
    """        self.app = FastAPI(""",
)

# Use router.add_event_handler instead of app.add_event_handler (or on_event)
events_logic = """        self.app.router.add_event_handler("startup", self._api_startup_event)
        self.app.router.add_event_handler("shutdown", self._api_shutdown_event)"""

content = content.replace(
    "        app.add_exception_handler(Exception, self.handle_generic_exception)",
    "        app.add_exception_handler(Exception, self.handle_generic_exception)\n" + events_logic,
)

with open("freqtrade/rpc/api_server/webserver.py", "w") as f:
    f.write(content)
