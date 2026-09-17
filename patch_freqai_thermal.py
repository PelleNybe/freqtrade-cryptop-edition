import re

with open("freqtrade/freqai/freqai_interface.py", "r") as f:
    content = f.read()

train_patch = """
    def start_scanning(self, *args, **kwargs) -> None:
        \"\"\"
        Start `self._start_scanning` in a separate thread
        \"\"\"
        _thread = threading.Thread(target=self._start_scanning, args=args, kwargs=kwargs)
        self._threads.append(_thread)
        _thread.start()

    def _check_thermal_throttle(self):
        \"\"\"
        Checks CPU temperature on edge devices (like Raspberry Pi 5).
        If temp > 75C, sleep to prevent thermal throttling from affecting the trade loop.
        \"\"\"
        try:
            with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
                temp = float(f.read()) / 1000.0
                if temp > 75.0:
                    logger.warning(f"[THERMAL THROTTLE] CPU at {temp:.1f}C. Pausing FreqAI training for 15s.")
                    time.sleep(15)
        except Exception:
            pass

    def _start_scanning(self, strategy: IStrategy) -> None:
        \"\"\"
        Function designed to constantly scan pairs for retraining on a separate thread (intracandle)
        to improve model youth. This function is agnostic to data preparation/collection/storage,
        it simply trains on what ever data is available in the self.dd.
        :param strategy: IStrategy = The user defined strategy class
        \"\"\"
        while not self._stop_event.is_set():
            time.sleep(1)

            # EDGE OPTIMIZATION: Thermal throttling check
            self._check_thermal_throttle()

            if not self.train_queue:
                continue"""

content = re.sub(
    r'    def start_scanning\(self, \*args, \*\*kwargs\) -> None:\n.*?if not self\.train_queue:\n                continue',
    train_patch,
    content,
    flags=re.DOTALL
)

with open("freqtrade/freqai/freqai_interface.py", "w") as f:
    f.write(content)
