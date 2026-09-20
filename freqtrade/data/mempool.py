import logging
import threading
import time
from typing import Any


logger = logging.getLogger(__name__)


class MempoolDaemon(threading.Thread):
    """
    Mempool Arbitrage Simulation Engine.
    Connects to an EVM WebSocket node and monitors pending transactions.
    Aggregates mempool activity to allow strategies to front-run or react to DEX pressure.
    """

    def __init__(self, config: dict[str, Any]):
        super().__init__(name="MempoolDaemon", daemon=True)
        self.config = config
        self.mempool_config = config.get("mempool", {})
        self.enabled = self.mempool_config.get("enabled", False)
        self.rpc_url = self.mempool_config.get("rpc_url", "ws://localhost:8546")

        self.web3 = None
        self._shutdown = threading.Event()

        # We will keep a sliding window of the last N pending tx hashes to gauge volume
        self.pending_txs = []
        self.max_cache = 1000

        if self.enabled:
            self._init_web3()

    def _init_web3(self):
        try:
            from web3 import Web3

            self.web3 = Web3(Web3.WebsocketProvider(self.rpc_url))
            if not self.web3.is_connected():
                logger.warning(f"Web3 failed to connect to {self.rpc_url}")
                self.enabled = False
            else:
                logger.info(f"Connected to Web3 Mempool at {self.rpc_url}")
        except ImportError:
            logger.error("web3 missing. Run `pip install web3` to use Mempool Arbitrage Engine.")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Web3 client: {e}")
            self.enabled = False

    def stop(self):
        self._shutdown.set()

    def run(self):
        if not self.enabled or not self.web3:
            return

        logger.info("Starting Mempool Daemon...")
        while not self._shutdown.is_set():
            try:
                # web3.py websockets block, so we use a short timeout or poll getBlock('pending')
                # For compatibility across nodes (Infura, local), polling 'pending' block is stable.
                pending_block = self.web3.eth.get_block("pending", full_transactions=False)

                tx_hashes = pending_block.get("transactions", [])
                if len(tx_hashes) > 0:
                    self._update_cache(tx_hashes)

            except Exception as e:
                logger.debug(f"Error fetching mempool: {e}")

            # Sleep briefly to not spam the RPC
            time.sleep(1)

    def _update_cache(self, txs: list[Any]):
        """Keep a rolling window of recent transaction hashes"""
        for tx in txs:
            tx_hex = tx.hex() if hasattr(tx, "hex") else str(tx)
            if tx_hex not in self.pending_txs:
                self.pending_txs.append(tx_hex)

        # Truncate
        if len(self.pending_txs) > self.max_cache:
            self.pending_txs = self.pending_txs[-self.max_cache :]

    def get_mempool_activity(self) -> float:
        """
        Returns a normalized score (0.0 to 1.0) of mempool activity based on max_cache.
        1.0 means the mempool cache is saturated (high activity).
        """
        if not self.enabled:
            return 0.0
        return len(self.pending_txs) / float(self.max_cache)
