import logging
import threading
import time

import requests


logger = logging.getLogger(__name__)


class OnChainRiskGuard:
    """
    DefiLlama On-Chain Risk Filter for Freqtrade - Crypto P Edition.
    Fetches macro TVL (Total Value Locked) and stablecoin flow data asynchronously.
    Strategies can query this module to dynamically adjust risk based on macro liquidity.
    """

    def __init__(self, update_interval_seconds: int = 3600) -> None:
        self.update_interval = update_interval_seconds
        self._global_tvl: float = 0.0
        self._last_update: float = 0.0
        self._running: bool = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._worker, name="DefiLlama_RiskGuard", daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread:
            self._thread.join(timeout=2)

    def _worker(self) -> None:
        logger.info("Starting DefiLlama OnChainRiskGuard background worker.")
        while self._running:
            try:
                # Fetch Global TVL from DefiLlama
                response = requests.get("https://api.llama.fi/charts", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        latest_entry = data[-1]
                        self._global_tvl = float(latest_entry.get("totalLiquidityUSD", 0.0))
                        self._last_update = time.time()
                        logger.debug(f"[DefiLlama] Global TVL updated: ${self._global_tvl:,.2f}")
                else:
                    logger.warning(f"[DefiLlama] Failed to fetch TVL data: {response.status_code}")
            except Exception as e:
                logger.warning(f"[DefiLlama] Error updating macro risk data: {e}")

            # Sleep in chunks to allow responsive shutdown
            for _ in range(self.update_interval):
                if not self._running:
                    break
                time.sleep(1)

    @property
    def global_tvl(self) -> float:
        """Returns the latest cached Global TVL in USD."""
        return self._global_tvl

    @property
    def last_update(self) -> float:
        """Returns the UNIX timestamp of the last successful TVL update."""
        return self._last_update


# Global instance
risk_guard = OnChainRiskGuard()
