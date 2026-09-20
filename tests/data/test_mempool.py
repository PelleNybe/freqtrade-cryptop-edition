import pytest
import time
from unittest.mock import patch, MagicMock
from freqtrade.data.mempool import MempoolDaemon
from freqtrade.data.dataprovider import DataProvider

@patch("freqtrade.data.mempool.Web3", create=True)
def test_mempool_daemon(mock_web3):
    # Mock Web3
    mock_w3_inst = MagicMock()
    mock_w3_inst.is_connected.return_value = True

    mock_tx = MagicMock()
    mock_tx.hex.return_value = "0x123"

    mock_w3_inst.eth.get_block.return_value = {'transactions': [mock_tx, "0x456"]}
    mock_web3.return_value = mock_w3_inst

    config = {
        "mempool": {
            "enabled": True,
            "rpc_url": "ws://localhost:8546"
        }
    }

    import sys
    sys.modules['web3'] = MagicMock()
    sys.modules['web3'].Web3 = mock_web3

    daemon = MempoolDaemon(config)
    assert daemon.enabled

    # Manually trigger loop logic
    daemon.web3 = mock_w3_inst

    # instead of running full thread, just call the logic
    pending = daemon.web3.eth.get_block('pending')
    daemon._update_cache(pending['transactions'])

    assert daemon.get_mempool_activity() == 2.0 / 1000.0

    daemon.stop()

def test_mempool_disabled():
    config = {"mempool": {"enabled": False}}
    daemon = MempoolDaemon(config)
    assert not daemon.enabled
    assert daemon.get_mempool_activity() == 0.0

def test_dataprovider_mempool_fallback():
    config = {}
    dp = DataProvider(config, None)
    assert dp.get_mempool_activity() == 0.0
