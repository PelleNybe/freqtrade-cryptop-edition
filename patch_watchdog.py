import re

with open("freqtrade/exchange/exchange_ws.py", "r") as f:
    content = f.read()

init_patch = """        self.klines_last_refresh: dict[PairWithTimeframe, float] = {}
        self.klines_last_request: dict[PairWithTimeframe, float] = {}

        # EDGE OPTIMIZATION: Silent-Disconnect Websocket Watchdog
        self._last_ws_message_time = time.time()
        self._watchdog_timeout_ms = 3000

        self._thread = Thread(name="ccxt_ws", target=self._start_forever)
        self._thread.start()
        self.__cleanup_called = False

        # Start watchdog task
        self._watchdog_thread = Thread(name="ws_watchdog", target=self._ws_watchdog, daemon=True)
        self._watchdog_thread.start()"""

content = re.sub(
    r'        self\.klines_last_refresh: dict\[PairWithTimeframe, float\] = \{\}\n        self\.klines_last_request: dict\[PairWithTimeframe, float\] = \{\}\n        self\._thread = Thread\(name="ccxt_ws", target=self\._start_forever\)\n        self\._thread\.start\(\)\n        self\.__cleanup_called = False',
    init_patch,
    content
)

watchdog_func = """    def _ws_watchdog(self) -> None:
        \"\"\"
        EDGE OPTIMIZATION: Silent-Disconnect Websocket Watchdog
        Forcefully recycles the websocket connection if no data is received within the timeout window.
        Crucial for mitigating silent stream freezes on Gate.io and KuCoin.
        \"\"\"
        while not self.__cleanup_called:
            time.sleep(1)
            elapsed = (time.time() - self._last_ws_message_time) * 1000
            if elapsed > self._watchdog_timeout_ms and len(self._klines_watching) > 0:
                logger.warning(f"[WS WATCHDOG] Stale connection detected. No data in {elapsed:.0f}ms. Restarting event loop...")
                self._last_ws_message_time = time.time()
                self._reset_ws()"""

content = re.sub(
    r'    def _start_forever\(self\) -> None:',
    watchdog_func + '\n\n    def _start_forever(self) -> None:',
    content
)

tick_patch = """    async def _async_get_candle_history(
        self, pair: str, timeframe: str, candle_type: CandleType
    ) -> None:
        if not self._ccxt_object.has["watchOHLCV"]:
            return

        while True:
            try:
                # EDGE OPTIMIZATION: Update watchdog timer on every tick
                self._last_ws_message_time = time.time()"""

content = re.sub(
    r'    async def _async_get_candle_history\(\n        self, pair: str, timeframe: str, candle_type: CandleType\n    \) -> None:\n        if not self\._ccxt_object\.has\["watchOHLCV"\]:\n            return\n\n        while True:\n            try:',
    tick_patch,
    content
)

with open("freqtrade/exchange/exchange_ws.py", "w") as f:
    f.write(content)
