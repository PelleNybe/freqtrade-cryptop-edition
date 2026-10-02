import logging
import sys
import tempfile
from pathlib import Path

import orjson
from fastapi import FastAPI


# Add project root to python path to allow importing freqtrade
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from freqtrade.configuration import Configuration
    from freqtrade.enums.runmode import RunMode
    from freqtrade.rpc.api_server.webserver import ApiServer
except ImportError:
    pass

logger = logging.getLogger(__name__)

# Default config needed to start FastAPI app via Vercel entrypoint
config_dict = {
    "runmode": "webserver",
    "exchange": {"name": "binance"},
    "api_server": {
        "enabled": True,
        "listen_ip_address": "0.0.0.0",  # noqa: S104
        "listen_port": 8080,
        "jwt_secret_key": "somethingRandomSomethingRandom123",
    },
}

err_msg = ""
try:
    with tempfile.NamedTemporaryFile("wb", delete=False) as f:
        f.write(orjson.dumps(config_dict))
        temp_config_path = f.name

    config = Configuration({"config": [temp_config_path]}, RunMode.WEBSERVER).get_config()

    # Initialize the ApiServer in standalone mode
    api_server = ApiServer(config, standalone=True)

    # Expose the FastAPI app
    app = api_server.app

    # Try to cleanup temporary file
    try:
        Path(temp_config_path).unlink()
    except OSError:
        pass

except Exception as err:
    err_msg = str(err)
    logger.exception(f"Error starting Freqtrade API Server for Vercel: {err}")
    # Provide a fallback app to prevent Vercel 500 crashes completely
    app = FastAPI()

    @app.get("/")
    def read_root():
        return {"error": "Failed to initialize Freqtrade API Server", "details": err_msg}
