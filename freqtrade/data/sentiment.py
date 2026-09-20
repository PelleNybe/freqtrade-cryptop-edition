import logging
import threading
import time
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any


logger = logging.getLogger(__name__)


class NLPSentimentDaemon(threading.Thread):
    """
    Hyper-Local NLP Sentiment Daemon (Quantized SLM).
    Periodically fetches RSS news, processes sentiment offline using a quantized SLM,
    and caches the sentiment score [-1.0 to 1.0] for strategies.
    """

    def __init__(self, config: dict[str, Any]):
        super().__init__(name="NLPSentimentDaemon", daemon=True)
        self.config = config
        self.sentiment_config = config.get("nlp_sentiment", {})
        self.enabled = self.sentiment_config.get("enabled", False)
        self.interval = self.sentiment_config.get("interval_sec", 300)
        self.rss_feeds = self.sentiment_config.get("rss_feeds", ["https://cointelegraph.com/rss"])
        self.model_path = self.sentiment_config.get(
            "model_path", "models/llama-2-7b-chat.Q4_K_M.gguf"
        )

        self.llm = None
        self._shutdown = threading.Event()

        # Cache of pair -> sentiment score
        self.sentiment_cache: dict[str, float] = {}
        # Global market sentiment
        self.global_sentiment: float = 0.0

        if self.enabled:
            self._init_model()

    def _init_model(self):
        try:
            from llama_cpp import Llama

            # Load the highly quantized SLM
            self.llm = Llama(model_path=self.model_path, verbose=False, n_ctx=512)
            logger.info(f"Loaded SLM from {self.model_path} for offline sentiment analysis.")
        except ImportError:
            logger.error(

                    "llama-cpp-python missing. Run `pip install llama-cpp-python` "
                    "to use NLP Sentiment Daemon."

            )
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to load SLM model at {self.model_path}: {e}")
            self.enabled = False

    def stop(self):
        self._shutdown.set()

    def run(self):
        if not self.enabled or not self.llm:
            return

        logger.info("Starting NLP Sentiment Daemon...")
        while not self._shutdown.is_set():
            try:
                self._update_sentiment()
            except Exception as e:
                logger.warning(f"Error updating sentiment: {e}")

            # Sleep in chunks to allow responsive shutdown
            for _ in range(self.interval):
                if self._shutdown.is_set():
                    break
                time.sleep(1)

    def _update_sentiment(self):
        news_items = []
        for feed_url in self.rss_feeds:
            try:
                req = urllib.request.Request(feed_url, headers={"User-Agent": "Mozilla/5.0"})  # noqa: S310
                with urllib.request.urlopen(req, timeout=10) as response:  # noqa: S310
                    xml_data = response.read()
                    root = ET.fromstring(xml_data)  # noqa: S314
                    for item in root.findall(".//item")[:5]:  # Take top 5 from each feed
                        title = item.findtext("title")
                        if title:
                            news_items.append(title)
            except Exception as e:
                logger.warning(f"Failed to fetch RSS feed {feed_url}: {e}")

        if not news_items:
            return

        # Simple prompt to rate sentiment
        scores = []
        for news in news_items:
            prompt = (
                f"Analyze the sentiment of the following crypto news headline and "
                f"respond with ONLY a single float number between -1.0 (extremely bearish) "
                f"and 1.0 (extremely bullish). Headline: '{news}'"
            )
            try:
                # Run inference
                output = self.llm(prompt, max_tokens=10, stop=["\n"], echo=False)
                result_text = output["choices"][0]["text"].strip()

                # Try to extract a float from the response
                import re

                match = re.search(r"[-+]?\d*\.\d+|\d+", result_text)
                if match:
                    score = float(match.group())
                    score = max(-1.0, min(1.0, score))
                    scores.append(score)
            except Exception as e:
                logger.debug(f"Failed to parse SLM output for sentiment: {e}")

        if scores:
            avg_score = sum(scores) / len(scores)
            self.global_sentiment = avg_score
            logger.info(f"Updated global market sentiment to: {self.global_sentiment:.2f}")

    def get_global_sentiment(self) -> float:
        return self.global_sentiment

    def get_pair_sentiment(self, pair: str) -> float:
        # For simplicity, fallback to global sentiment if pair-specific isn't parsed
        return self.sentiment_cache.get(pair, self.global_sentiment)
