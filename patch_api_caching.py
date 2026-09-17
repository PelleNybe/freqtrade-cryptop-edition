import re

with open("freqtrade/rpc/api_server/api_trading.py", "r") as f:
    content = f.read()

import_patch = """import logging
from copy import deepcopy

from cachetools import cached, TTLCache"""

content = content.replace("import logging\nfrom copy import deepcopy", import_patch)

# Create a cache object
cache_init = """from freqtrade.rpc.rpc import RPCException

# EDGE OPTIMIZATION: In-memory TTL cache for high-frequency GET requests
api_response_cache = TTLCache(maxsize=100, ttl=5)
"""

content = content.replace("from freqtrade.rpc.rpc import RPCException", cache_init)

# Use simple replacement instead of regex for safety
old_status = """@router.get(
    "/status",
    response_model=list[OpenTradeSchema],
    tags=["Trading-info"],
    dependencies=[Depends(RateLimiter(max_calls=20, time_seconds=60))],
)
def status(rpc: RPC = Depends(get_rpc)):
    try:
        return rpc._rpc_trade_status()
    except RPCException:
        return []"""

new_status = """@router.get(
    "/status",
    response_model=list[OpenTradeSchema],
    tags=["Trading-info"],
    dependencies=[Depends(RateLimiter(max_calls=20, time_seconds=60))],
)
@cached(cache=api_response_cache)
def status(rpc: RPC = Depends(get_rpc)):
    try:
        return rpc._rpc_trade_status()
    except RPCException:
        return []"""

content = content.replace(old_status, new_status)

old_profit = """@router.get(
    "/profit",
    response_model=ProfitSchema,
    tags=["Trading-info"],
    dependencies=[Depends(RateLimiter(max_calls=20, time_seconds=60))],
)
def profit(rpc: RPC = Depends(get_rpc), config=Depends(get_config)):
    try:
        return rpc._rpc_trade_statistics(
            config["stake_currency"], config.get("fiat_display_currency")
        )
    except RPCException as e:
        raise HTTPException(status_code=502, detail=str(e))"""

new_profit = """@router.get(
    "/profit",
    response_model=ProfitSchema,
    tags=["Trading-info"],
    dependencies=[Depends(RateLimiter(max_calls=20, time_seconds=60))],
)
@cached(cache=api_response_cache)
def profit(rpc: RPC = Depends(get_rpc), config=Depends(get_config)):
    try:
        return rpc._rpc_trade_statistics(
            config["stake_currency"], config.get("fiat_display_currency")
        )
    except RPCException as e:
        raise HTTPException(status_code=502, detail=str(e))"""

content = content.replace(old_profit, new_profit)

with open("freqtrade/rpc/api_server/api_trading.py", "w") as f:
    f.write(content)
