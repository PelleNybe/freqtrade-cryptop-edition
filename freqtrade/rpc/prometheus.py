import logging
import threading
import time

from prometheus_client import Gauge, start_http_server

from freqtrade.persistence import Trade
from freqtrade.rpc import RPC
from freqtrade.rpc.rpc_types import RPCSendMsg


logger = logging.getLogger(__name__)


class PrometheusExporter(RPC):
    """
    Native Prometheus Metrics Exporter for Freqtrade - Crypto P Edition.
    Exposes a local /metrics endpoint for Grafana hardware and trade telemetry.
    """

    def __init__(self, freqtrade) -> None:
        super().__init__(freqtrade)
        self._config = freqtrade.config
        self.prom_config = self._config.get("prometheus", {})
        self.enabled = self.prom_config.get("enabled", False)

        if self.enabled:
            port = self.prom_config.get("port", 8080)
            logger.info(f"Prometheus Exporter enabled. Starting server on port {port}...")

            try:
                # Trade Metrics
                self.open_trades_gauge = Gauge(
                    "freqtrade_open_trades", "Current number of open trades"
                )
                self.total_profit_gauge = Gauge(
                    "freqtrade_total_profit_usd", "Total absolute profit"
                )

                # Edge Hardware Metrics
                self.cpu_temp_gauge = Gauge("freqtrade_cpu_temp_c", "CPU Temperature (C)")
                self.ram_usage_gauge = Gauge("freqtrade_ram_usage_pct", "RAM Usage %")

                start_http_server(port)

                self._running = True
                self._thread = threading.Thread(target=self._update_metrics_loop, daemon=True)
                self._thread.start()

            except Exception as e:
                logger.error(f"Failed to start Prometheus Exporter: {e}")
                self.enabled = False

    def _update_metrics_loop(self) -> None:
        import psutil

        while self._running:
            try:
                # Update Trade Metrics
                open_trades = Trade.get_open_trades()
                self.open_trades_gauge.set(len(open_trades))

                # Update Hardware Metrics
                try:
                    from pathlib import Path
                    with Path("/sys/class/thermal/thermal_zone0/temp").open() as f:
                        temp = float(f.read()) / 1000.0
                        self.cpu_temp_gauge.set(temp)
                except Exception as e:
                    logger.debug(f"Thermal check failed: {e}")


                self.ram_usage_gauge.set(psutil.virtual_memory().percent)

            except Exception as e:
                logger.debug(f"Error updating Prometheus metrics: {e}")

            time.sleep(15)

    def cleanup(self) -> None:
        if self.enabled:
            self._running = False
            if hasattr(self, "_thread"):
                self._thread.join(timeout=2)

    def send_msg(self, msg: RPCSendMsg) -> None:
        pass
        # Prometheus operates by pulling, so we don't actively push via send_msg
