with open("freqtrade/rpc/api_server/api_trading.py") as f:
    content = f.read()

# Fix the placement of the cached_response decorator
content = content.replace(
    '@router.get("/profit", response_model=Profit, tags=["Trading"])',
    '@router.get("/profit", response_model=Profit, tags=["Trading"])\n@cached_response(ttl_seconds=15)',
)

content = content.replace(
    '@router.get("/performance", response_model=list[PerformanceEntry], tags=["Trading"])',
    '@router.get("/performance", response_model=list[PerformanceEntry], tags=["Trading"])\n@cached_response(ttl_seconds=15)',
)

with open("freqtrade/rpc/api_server/api_trading.py", "w") as f:
    f.write(content)
