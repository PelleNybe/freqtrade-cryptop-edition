import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from freqtrade.constants import Config, LongShort
from freqtrade.persistence import Trade
from freqtrade.plugins.protections import IProtection, ProtectionReturn


if TYPE_CHECKING:
    from freqtrade.wallets import Wallets

logger = logging.getLogger(__name__)


class ConsecutiveWinGuard(IProtection):
    has_global_stop: bool = True
    has_local_stop: bool = True

    def __init__(
        self, config: Config, protection_config: dict[str, Any], wallets: "Wallets | None" = None
    ) -> None:
        super().__init__(config, protection_config, wallets)

        self._trade_limit = protection_config.get("trade_limit", 3)
        self._disable_global_stop = protection_config.get("only_per_pair", False)
        self._only_per_side = protection_config.get("only_per_side", False)

    def short_desc(self) -> str:
        return (
            f"{self.name} - Stops trading if {self._trade_limit} consecutive wins occur "
            f"within {self.lookback_period_str}."
        )

    def _reason(self) -> str:
        return (
            f"{self._trade_limit} consecutive wins in {self.lookback_period_str}, "
            f"locking {self.unlock_reason_time_element}."
        )

    def _consecutive_win_guard(
        self, date_now: datetime, pair: str | None, side: LongShort
    ) -> ProtectionReturn | None:
        look_back_until = date_now - timedelta(minutes=self._lookback_period)

        trades = Trade.get_trades_proxy(pair=pair, is_open=False, close_date=look_back_until)

        if self._only_per_side:
            trades = [trade for trade in trades if trade.trade_direction == side]

        if len(trades) < self._trade_limit:
            return None

        # Sort trades by close_date descending
        trades = sorted(trades, key=lambda t: t.close_date, reverse=True)  # type: ignore

        consecutive_wins = 0
        win_trades = []
        for trade in trades:
            if trade.close_profit is not None and trade.close_profit > 0:
                consecutive_wins += 1
                win_trades.append(trade)
            else:
                break  # Broken consecutive streak

        if consecutive_wins >= self._trade_limit:
            self.log_once(
                f"Trading stopped due to {self._trade_limit} consecutive wins "
                f"within {self._lookback_period} minutes.",
                logger.info,
            )
            until = self.calculate_lock_end(win_trades)
            return ProtectionReturn(
                lock=True,
                until=until,
                reason=self._reason(),
                lock_side=(side if self._only_per_side else "*"),
            )

        return None

    def global_stop(self, date_now: datetime, side: LongShort) -> ProtectionReturn | None:
        if self._disable_global_stop:
            return None
        return self._consecutive_win_guard(date_now, None, side)

    def stop_per_pair(
        self, pair: str, date_now: datetime, side: LongShort
    ) -> ProtectionReturn | None:
        return self._consecutive_win_guard(date_now, pair, side)
