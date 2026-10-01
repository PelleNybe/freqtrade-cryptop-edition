with open("freqtrade/rpc/api_server/api_trading.py") as f:
    content = f.read()

content = content.replace(
    "@cached(cache=api_response_cache)", "# @cached(cache=api_response_cache)"
)

with open("freqtrade/rpc/api_server/api_trading.py", "w") as f:
    f.write(content)
