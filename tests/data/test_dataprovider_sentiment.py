import pytest
from unittest.mock import MagicMock
from freqtrade.data.dataprovider import DataProvider

def test_dataprovider_sentiment_fallback():
    config = {}
    dp = DataProvider(config, None)

    # Defaults to 0.0 when not enabled
    assert dp.get_global_sentiment() == 0.0
    assert dp.get_pair_sentiment("BTC/USDT") == 0.0

def test_dataprovider_sentiment_mocked():
    config = {
        "nlp_sentiment": {
            "enabled": True,
        }
    }
    dp = DataProvider(config, None)
    # the daemon's start should have been called, but since we didn't mock llama_cpp it fails to initialize and sets enabled=False
    assert not dp._sentiment_daemon.enabled

    # Manually inject mock daemon logic
    dp._sentiment_daemon.global_sentiment = 0.5
    dp._sentiment_daemon.sentiment_cache["BTC/USDT"] = 0.7

    assert dp.get_global_sentiment() == 0.5
    assert dp.get_pair_sentiment("BTC/USDT") == 0.7
    assert dp.get_pair_sentiment("ETH/USDT") == 0.5 # fallbacks to global
