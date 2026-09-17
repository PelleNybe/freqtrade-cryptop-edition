import re

with open("freqtrade/exchange/exchange.py", "r") as f:
    content = f.read()

worker_patch = """    def _start_funding_worker(self):
        \"\"\"
        EDGE OPTIMIZATION: Asynchronous Futures Funding Rate Cache
        Spawns a dedicated background thread to continuously fetch Mark Prices and Funding Rates.
        This allows strategies to evaluate heavy futures rates without incurring blocking API lag on the main thread.
        \"\"\"
        import threading
        import time

        def _funding_loop():
            logger.info("Started background futures funding rate cacher.")
            while True:
                try:
                    if self._api:
                        markets = self.get_markets()
                        futures = [m for m in markets.keys() if self.market_is_future(markets[m])]

                        if futures and self._ft_has.get("fetchFundingRates", False):
                            rates = self._api.fetch_funding_rates(futures)
                            for pair, data in rates.items():
                                self._funding_rate_cache[pair] = {
                                    "fundingRate": data.get("fundingRate", 0),
                                    "markPrice": data.get("markPrice", 0),
                                    "timestamp": dt_now().timestamp()
                                }
                except Exception as e:
                    logger.debug(f"Funding rate cacher error: {e}")
                time.sleep(30) # Refresh every 30s

        self._funding_thread = threading.Thread(target=_funding_loop, daemon=True)
        self._funding_thread.start()

    def get_cached_funding_rate(self, pair: str) -> dict:
        \"\"\"
        Returns the background-cached funding rate and mark price for a pair.
        Returns a dict: {'fundingRate': float, 'markPrice': float, 'timestamp': float}
        \"\"\"
        return self._funding_rate_cache.get(pair, {"fundingRate": 0.0, "markPrice": 0.0, "timestamp": 0.0})"""

content = re.sub(
    r'    def validate_freqai\(self, config: Config\) -> None:',
    worker_patch + '\n\n    def validate_freqai(self, config: Config) -> None:',
    content
)

with open("freqtrade/exchange/exchange.py", "w") as f:
    f.write(content)
