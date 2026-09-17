"""
Spike pairlist filter
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


class SpikeFilter(IPairList):
    """
    Filters pairs that had an abnormal spike (pump/dump) recently
    """

    supports_backtesting = SupportsBacktesting.NO

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self._days = self._pairlistconfig.get("lookback_days", 3)
        self._max_spike_percentage = self._pairlistconfig.get("max_spike_percentage", 20.0)

        self._refresh_period = self._pairlistconfig.get("refresh_period", 1440)
        self._def_candletype = self._config["candle_type_def"]
        self._pair_cache: FtTTLCache = FtTTLCache(maxsize=1000, ttl=self._refresh_period)

        candle_limit = self._exchange.ohlcv_candle_limit("1d", self._def_candletype)
        if self._days < 1:
            raise OperationalException("SpikeFilter requires lookback_days to be >= 1")
        if self._days > candle_limit:
            raise OperationalException(
                "SpikeFilter requires lookback_days to not "
                f"exceed exchange max request size ({candle_limit})"
            )

    @property
    def needstickers(self) -> bool:
        return False

    def short_desc(self) -> str:
        return (
            f"{self.name} - Filtering pairs with spikes > {self._max_spike_percentage}% "
            f"over the last {self._days} {plural(self._days, 'day')}."
        )

    @staticmethod
    def description() -> str:
        return "Filter pairs by recent extreme price movements (spikes)."

    @staticmethod
    def available_parameters() -> dict[str, PairlistParameter]:
        return {
            "lookback_days": {
                "type": "number",
                "default": 3,
                "description": "Lookback Days",
                "help": "Number of days to check for spikes.",
            },
            "max_spike_percentage": {
                "type": "number",
                "default": 20.0,
                "description": "Max Spike Percentage",
                "help": "Max allowed price change (pump or dump) within a day as a percentage.",
            },
            **IPairList.refresh_period_parameter(),
        }

    def filter_pairlist(self, pairlist: list[str], tickers: Tickers) -> list[str]:
        needed_pairs: ListPairsWithTimeframes = [
            (p, "1d", self._def_candletype) for p in pairlist if p not in self._pair_cache
        ]

        since_ms = dt_ts(dt_floor_day(dt_now()) - timedelta(days=self._days))
        candles = self._exchange.refresh_ohlcv_with_cache(needed_pairs, since_ms=since_ms)

        resulting_pairlist: list[str] = []

        for p in pairlist:
            daily_candles = candles.get((p, "1d", self._def_candletype), None)

            max_spike = self._calculate_max_spike(p, daily_candles)

            if max_spike is not None:
                if self._validate_pair_loc(p, max_spike):
                    resulting_pairlist.append(p)
            else:
                self.log_once(f"Removed {p} from whitelist, no candles found.", logger.info)

        return resulting_pairlist

    def _calculate_max_spike(self, pair: str, daily_candles: pd.DataFrame) -> float | None:
        if (max_spike := self._pair_cache.get(pair, None)) is not None:
            return max_spike

        if daily_candles is not None and not daily_candles.empty:
            # Calculate the maximum percentage change (high vs low) in a single day
            daily_spikes = (
                (daily_candles["high"] - daily_candles["low"]) / daily_candles["low"]
            ) * 100.0
            max_spike_val = daily_spikes.max()

            if pd.isna(max_spike_val):
                return None

            self._pair_cache[pair] = max_spike_val
            return max_spike_val
        else:
            return None

    def _validate_pair_loc(self, pair: str, max_spike: float) -> bool:
        if max_spike <= self._max_spike_percentage:
            return True
        else:
            self.log_once(
                f"Removed {pair} from whitelist, because it had a spike of "
                f"{max_spike:.3f}% which exceeds limit of {self._max_spike_percentage}%.",
                logger.info,
            )
            return False
