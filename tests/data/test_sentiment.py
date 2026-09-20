import pytest
from unittest.mock import patch, MagicMock
from freqtrade.data.sentiment import NLPSentimentDaemon

@patch("freqtrade.data.sentiment.urllib.request.urlopen")
def test_nlp_sentiment_daemon(mock_urlopen):
    # Mock LLM and response
    mock_llm = MagicMock()
    mock_llm.return_value = {'choices': [{'text': "0.8"}]}

    mock_response = MagicMock()
    mock_response.read.return_value = b"<?xml version='1.0'?><rss><channel><item><title>Bitcoin to the moon</title></item></channel></rss>"
    mock_response.__enter__.return_value = mock_response
    mock_urlopen.return_value = mock_response

    config = {
        "nlp_sentiment": {
            "enabled": True,
            "interval_sec": 1,
            "rss_feeds": ["http://test.com/rss"]
        }
    }

    with patch("freqtrade.data.sentiment.Llama", return_value=mock_llm, create=True) as mock_llama:
        import sys
        sys.modules['llama_cpp'] = MagicMock()
        sys.modules['llama_cpp'].Llama = mock_llama

        daemon = NLPSentimentDaemon(config)
        assert daemon.enabled

        daemon._update_sentiment()

        # 0.8 parsed correctly
        assert daemon.get_global_sentiment() == 0.8

        # Cleanup
        daemon.stop()
