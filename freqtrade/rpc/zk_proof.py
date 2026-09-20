import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any

from freqtrade.persistence import Trade


logger = logging.getLogger(__name__)


class ZKTradeProver:
    """
    Zero-Knowledge (ZK) Trade Performance Proofs.
    Generates a verifiable cryptographic commitment for a closed trade
    without revealing exact API keys, strategies, or full trade history.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.enabled = config.get("zk_proofs", {}).get("enabled", False)
        self.secret_key_path = Path(config.get("user_data_dir", "user_data")) / "zk_secret.key"
        self._secret = None

        if self.enabled:
            self._load_or_generate_secret()

    def _load_or_generate_secret(self):
        if not self.secret_key_path.exists():
            # Generate a 32-byte cryptographic random secret
            self._secret = os.urandom(32).hex()
            try:
                with self.secret_key_path.open("w") as f:
                    f.write(self._secret)
                # Restrict permissions for security
                self.secret_key_path.chmod(0o600)
                logger.info(f"Generated new ZK secret key at {self.secret_key_path}")
            except Exception as e:
                logger.error(f"Failed to write ZK secret key: {e}")
                self.enabled = False
        else:
            try:
                with self.secret_key_path.open() as f:
                    self._secret = f.read().strip()
            except Exception as e:
                logger.error(f"Failed to read ZK secret key: {e}")
                self.enabled = False

    def generate_proof(self, trade: Trade) -> dict[str, Any]:
        """
        Generates a basic hash-based commitment (ZK-like proof).
        In a full Web3 implementation, this would generate a SNARK.
        Here we generate a Pederson-like commitment: Hash(TradeData || Secret).
        """
        if not self.enabled or not self._secret:
            return {}

        # Public inputs we want to prove
        public_inputs = {
            "pair": trade.pair,
            "is_short": trade.is_short,
            "profit_ratio": round(trade.close_profit, 4) if trade.close_profit else 0.0,
            "trade_duration_s": (trade.close_date - trade.open_date).total_seconds()
            if trade.close_date and trade.open_date
            else 0,
            "exit_reason": trade.exit_reason,
        }

        # Private inputs we are committing to
        private_inputs = {
            "trade_id": trade.id,
            "open_rate": trade.open_rate,
            "close_rate": trade.close_rate,
            "stake_amount": trade.stake_amount,
            "strategy": trade.strategy,
        }

        # Create commitment payload
        payload = json.dumps(
            {"public": public_inputs, "private": private_inputs, "secret": self._secret},
            sort_keys=True,
        )

        commitment = hashlib.sha256(payload.encode("utf-8")).hexdigest()

        return {"zk_commitment": commitment, "public_inputs": public_inputs}
