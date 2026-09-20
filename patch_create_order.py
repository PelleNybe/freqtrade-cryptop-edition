import re

with open("freqtrade/exchange/exchange.py", "r") as f:
    content = f.read()

# Add logic to support stop_loss/take_profit params in create_order to allow edge-safe native trailing stops / OCOs
order_patch = """    def create_order(
        self,
        *,
        pair: str,
        ordertype: str,
        side: BuySell,
        amount: float,
        rate: float,
        leverage: float,
        time_in_force: str = "GTC",
        reduceOnly: bool = False,
        initial_order: bool = True,
        stop_price: float | None = None,
        take_profit_price: float | None = None,
    ) -> CcxtOrder:
        if self._config["dry_run"]:
            dry_order = self.create_dry_run_order(
                pair, ordertype, side, amount, self.price_to_precision(pair, rate), leverage
            )
            return dry_order

        params = self._get_params(side, ordertype, leverage, reduceOnly, time_in_force)

        # EDGE OPTIMIZATION: Exchange-Native OCO / Trailing Stops
        # Passes trigger prices natively to CCXT so the exchange handles stops,
        # protecting capital if the Edge device loses network connectivity.
        if stop_price:
            params["stopPrice"] = self.price_to_precision(pair, stop_price)
        if take_profit_price:
            params["takeProfitPrice"] = self.price_to_precision(pair, take_profit_price)"""

content = re.sub(
    r'    def create_order\(\n        self,\n        \*,\n        pair: str,\n        ordertype: str,\n        side: BuySell,\n        amount: float,\n        rate: float,\n        leverage: float,\n        time_in_force: str = "GTC",\n        reduceOnly: bool = False,\n        initial_order: bool = True,\n    \) -> CcxtOrder:\n        if self\._config\["dry_run"\]:\n            dry_order = self\.create_dry_run_order\(\n                pair, ordertype, side, amount, self\.price_to_precision\(pair, rate\), leverage\n            \)\n            return dry_order\n\n        params = self\._get_params\(side, ordertype, leverage, reduceOnly, time_in_force\)',
    order_patch,
    content
)

with open("freqtrade/exchange/exchange.py", "w") as f:
    f.write(content)
