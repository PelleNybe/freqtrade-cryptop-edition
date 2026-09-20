import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from freqtrade.constants import Config, LongShort
from freqtrade.persistence import Trade
from freqtrade.plugins.protections import IProtection, ProtectionReturn


if TYPE_CHECKING:
    from freqtrade.wallets import Wallets

logger = logging.getLogger(__name__)


class TakeProfitGuard(IProtection):
    has_global_stop: bool = True
    has_local_stop: bool = False

    def __init__(
        self, config: Config, protection_config: dict[str, Any], wallets: "Wallets | None" = None
    ) -> None:
        super().__init__(config, protection_config, wallets)

        self._target_profit_abs = protection_config.get("target_profit_abs", None)
        self._target_profit_pct = protection_config.get("target_profit_pct", None)

        if self._target_profit_abs is None and self._target_profit_pct is None:
            logger.warning(
                f"{self.name} initialized without target_profit_abs or target_profit_pct."
            )

        self._trade_limit = protection_config.get("trade_limit", 1)

    def short_desc(self) -> str:
        target = (
            f"{self._target_profit_abs} abs"
            if self._target_profit_abs
            else f"{self._target_profit_pct}%"
        )
        return (
            f"{self.name} - Take Profit Guard, stops trading if profit > {target} "
            f"within {self.lookback_period_str}."
        )

    def _reason(self, profit: float, is_abs: bool = True) -> str:
        target = self._target_profit_abs if is_abs else self._target_profit_pct
        unit = "" if is_abs else "%"
        return (
            f"Profit {profit:.2f}{unit} reached target {target}{unit} "
            f"in {self.lookback_period_str}, locking {self.unlock_reason_time_element}."
        )

    def _take_profit(self, date_now: datetime) -> ProtectionReturn | None:
        look_back_until = date_now - timedelta(minutes=self._lookback_period)

        trades = Trade.get_trades_proxy(is_open=False, close_date=look_back_until)

        if len(trades) < self._trade_limit:
            return None

        # Check absolute profit
        if self._target_profit_abs is not None:
            profit_abs = sum(t.close_profit_abs for t in trades if t.close_profit_abs)
            if profit_abs >= self._target_profit_abs:
                self.log_once(
                    f"Trading stopped due to hitting Take Profit: {profit_abs:.2f} >= "
                    f"{self._target_profit_abs} "
                    f"within {self._lookback_period} minutes.",
                    logger.info,
                )
                until = self.calculate_lock_end(trades)
                return ProtectionReturn(
                    lock=True,
                    until=until,
                    reason=self._reason(profit_abs, True),
                )

        # Check percentage profit based on starting balance
        if self._target_profit_pct is not None and self._wallets:
            profit_abs = sum(t.close_profit_abs for t in trades if t.close_profit_abs)
            current_balance = self._wallets.get_total(self._config["stake_currency"])
            starting_balance = current_balance - profit_abs

            if starting_balance > 0:
                profit_pct = (profit_abs / starting_balance) * 100.0
                if profit_pct >= self._target_profit_pct:
                    self.log_once(
                        f"Trading stopped due to hitting Take Profit Pct: {profit_pct:.2f}% >= "
                        f"{self._target_profit_pct}% "
                        f"within {self._lookback_period} minutes.",
                        logger.info,
                    )
                    until = self.calculate_lock_end(trades)
                    return ProtectionReturn(
                        lock=True,
                        until=until,
                        reason=self._reason(profit_pct, False),
                    )

        return None

    def global_stop(self, date_now: datetime, side: LongShort) -> ProtectionReturn | None:
        return self._take_profit(date_now)

    def stop_per_pair(
        self, pair: str, date_now: datetime, side: LongShort
    ) -> ProtectionReturn | None:
        return None
