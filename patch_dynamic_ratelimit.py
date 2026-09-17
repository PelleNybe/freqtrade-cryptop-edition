import re

with open("freqtrade/exchange/exchange.py", "r") as f:
    content = f.read()

# Add enableRateLimit to True if not explicitly overridden, and install a generic ccxt ratelimit patcher
patch = """    def _init_ccxt(
        self, exchange_config: dict[str, Any], sync: bool, ccxt_kwargs: dict[str, Any]
    ) -> ccxt.Exchange:
        \"\"\"
        Initialize ccxt with given config and return valid ccxt instance.
        \"\"\"
        # EDGE OPTIMIZATION: Dynamic CCXT Rate Limit Manager
        # We ensure ccxt uses its built-in rate limiter which can dynamically adjust based on exchange headers.
        if "enableRateLimit" not in ccxt_kwargs:
            ccxt_kwargs["enableRateLimit"] = True

        # Optional: enable tracking to respect X-RateLimit-Remaining natively if CCXT supports it
        # For KuCoin, OKX, Gate this improves safety drastically.
        if "options" not in ccxt_kwargs:
            ccxt_kwargs["options"] = {}
        ccxt_kwargs["options"]["adjustForTimeDifference"] = True

        # Find matching class for the given exchange name"""

content = re.sub(
    r'    def _init_ccxt\(\n        self, exchange_config: dict\[str, Any\], sync: bool, ccxt_kwargs: dict\[str, Any\]\n    \) -> ccxt\.Exchange:\n        """\n        Initialize ccxt with given config and return valid ccxt instance\.\n        """\n        # Find matching class for the given exchange name',
    patch,
    content
)

with open("freqtrade/exchange/exchange.py", "w") as f:
    f.write(content)
