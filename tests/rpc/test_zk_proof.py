import pytest
import os
import json
from pathlib import Path
from unittest.mock import patch, MagicMock
from freqtrade.rpc.zk_proof import ZKTradeProver
from freqtrade.persistence import Trade
from datetime import datetime, UTC

def test_zk_proof_generation(tmp_path):
    config = {
        "zk_proofs": {"enabled": True},
        "user_data_dir": str(tmp_path)
    }

    prover = ZKTradeProver(config)
    assert prover.enabled
    assert prover._secret is not None
    assert len(prover._secret) == 64 # 32 bytes hex

    # Mock a trade
    trade = MagicMock(spec=Trade)
    trade.pair = "BTC/USDT"
    trade.is_short = False
    trade.close_profit = 0.05
    trade.open_date = datetime(2024, 1, 1, tzinfo=UTC)
    trade.close_date = datetime(2024, 1, 1, 1, tzinfo=UTC) # 1 hour
    trade.exit_reason = "roi"
    trade.id = 1
    trade.open_rate = 40000.0
    trade.close_rate = 42000.0
    trade.stake_amount = 100.0
    trade.strategy = "MyStrat"

    proof = prover.generate_proof(trade)

    assert "zk_commitment" in proof
    assert "public_inputs" in proof

    public_inputs = proof["public_inputs"]
    assert public_inputs["pair"] == "BTC/USDT"
    assert public_inputs["profit_ratio"] == 0.05
    assert public_inputs["trade_duration_s"] == 3600
    assert public_inputs["exit_reason"] == "roi"

def test_zk_proof_disabled(tmp_path):
    config = {
        "zk_proofs": {"enabled": False},
        "user_data_dir": str(tmp_path)
    }

    prover = ZKTradeProver(config)
    assert not prover.enabled
    assert prover.generate_proof(MagicMock()) == {}

def test_zk_proof_reloads_secret(tmp_path):
    secret_path = tmp_path / "zk_secret.key"
    with open(secret_path, 'w') as f:
        f.write("my_test_secret")

    config = {
        "zk_proofs": {"enabled": True},
        "user_data_dir": str(tmp_path)
    }

    prover = ZKTradeProver(config)
    assert prover.enabled
    assert prover._secret == "my_test_secret"
