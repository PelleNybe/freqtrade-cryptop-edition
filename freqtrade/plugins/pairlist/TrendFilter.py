"""
Trend pairlist filter
"""

import logging
from datetime import timedelta

import pandas as pd

from freqtrade.constants import ListPairsWithTimeframes
from freqtrade.exceptions import OperationalException
from freqtrade.exchange.exchange_types import Tickers
from freqtrade.misc import plural
from freqtrade.plugins.pairlist.IPairList import IPairList, PairlistParameter, SupportsBacktesting
from freqtrade.util import FtTTLCache, dt_floor_day, dt_now, dt_ts


logger = logging.getLogger(__name__)


class TrendFilter(IPairList):
    """
    Filters pairs by Trend (Simple Moving Average or Exponential Moving Average)
    """

    supports_backtesting = SupportsBacktesting.NO

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._days = self._pairlistconfig.get("lookback_days", 14)
        self._trend_type = self._pairlistconfig.get("trend_type", "sma")
        if self._trend_type not in ["sma", "ema"]:
            raise OperationalException("TrendFilter requires trend_type to be 'sma' or 'ema'")

        self._minimum_trend_strength = self._pairlistconfig.get("minimum_trend_strength", 0.0)
        self._sort_direction = self._pairlistconfig.get("sort_direction", None)

        self._refresh_period = self._pairlistconfig.get("refresh_period", 1440)
        self._def_candletype = self._config["candle_type_def"]
        self._pair_cache: FtTTLCache = FtTTLCache(maxsize=1000, ttl=self._refresh_period)

        candle_limit = self._exchange.ohlcv_candle_limit("1d", self._def_candletype)
        if self._days < 1:
            raise OperationalException("TrendFilter requires lookback_days to be >= 1")
        if self._days > candle_limit:
            raise OperationalException(
                "TrendFilter requires lookback_days to not "
                f"exceed exchange max request size ({candle_limit})"
            )

    @property
    def needstickers(self) -> bool:
        return False

    def short_desc(self) -> str:
        return (
            f"{self.name} - Filtering pairs by {self._trend_type.upper()} "
            f"trend over the last {self._days} {plural(self._days, 'day')}."
        )

    @staticmethod
    def description() -> str:
        return "Filter pairs by their recent trend (SMA/EMA)."

    @staticmethod
    def available_parameters() -> dict[str, PairlistParameter]:
        return {
            "lookback_days": {
                "type": "number",
                "default": 14,
                "description": "Lookback Days",
                "help": "Number of days to calculate the trend.",
            },
            "trend_type": {
                "type": "option",
                "default": "sma",
                "options": ["sma", "ema"],
                "description": "Trend Type",
                "help": "Trend type (SMA or EMA).",
            },
            "minimum_trend_strength": {
                "type": "number",
                "default": 0.0,
                "description": "Minimum Trend Strength",
                "help": "Minimum trend strength (current price vs moving average) as a percentage.",
            },
            "sort_direction": {
                "type": "option",
                "default": None,
                "options": ["", "asc", "desc"],
                "description": "Sort pairlist",
                "help": "Sort Pairlist ascending or descending by trend strength.",
            },
            **IPairList.refresh_period_parameter(),
        }

    def filter_pairlist(self, pairlist: list[str], tickers: Tickers) -> list[str]:
        needed_pairs: ListPairsWithTimeframes = [
            (p, "1d", self._def_candletype) for p in pairlist if p not in self._pair_cache
        ]

        # Need more than lookback_days to calculate moving averages properly, especially EMA
        fetch_days = self._days * 2 if self._trend_type == "ema" else self._days
        since_ms = dt_ts(dt_floor_day(dt_now()) - timedelta(days=fetch_days))
        candles = self._exchange.refresh_ohlcv_with_cache(needed_pairs, since_ms=since_ms)

        resulting_pairlist: list[str] = []
        trend_strengths: dict[str, float] = {}

        for p in pairlist:
            daily_candles = candles.get((p, "1d", self._def_candletype), None)

            trend_strength = self._calculate_trend(p, daily_candles)

            if trend_strength is not None:
                if self._validate_pair_loc(p, trend_strength):
                    resulting_pairlist.append(p)
                    trend_strengths[p] = trend_strength
            else:
                self.log_once(
                    f"Removed {p} from whitelist, no candles found or insufficient data.",
                    logger.info,
                )

        if self._sort_direction in ["asc", "desc"]:
            resulting_pairlist = sorted(
                resulting_pairlist,
                key=lambda p: trend_strengths.get(p, 0.0),
                reverse=self._sort_direction == "desc",
            )
        return resulting_pairlist

    def _calculate_trend(self, pair: str, daily_candles: pd.DataFrame) -> float | None:
        if (trend_strength := self._pair_cache.get(pair, None)) is not None:
            return trend_strength

        if (
            daily_candles is not None
            and not daily_candles.empty
            and len(daily_candles) >= self._days
        ):
            if self._trend_type == "sma":
                ma = daily_candles["close"].rolling(window=self._days).mean().iloc[-1]
            else:  # ema
                ma = daily_candles["close"].ewm(span=self._days, adjust=False).mean().iloc[-1]

            current_close = daily_candles["close"].iloc[-1]
            if pd.isna(ma) or ma == 0:
                return None

            trend_strength = ((current_close - ma) / ma) * 100.0
            self._pair_cache[pair] = trend_strength
            return trend_strength
        else:
            return None

    def _validate_pair_loc(self, pair: str, trend_strength: float) -> bool:
        if trend_strength >= self._minimum_trend_strength:
            return True
        else:
            self.log_once(
                f"Removed {pair} from whitelist, because trend strength "
                f"{trend_strength:.3f}% is below minimum {self._minimum_trend_strength}%.",
                logger.info,
            )
            return False
