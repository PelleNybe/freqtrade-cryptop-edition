import re

with open('freqtrade/freqai/freqai_interface.py', 'r') as f:
    content = f.read()

# Add a deque to the FreqaiInterface init
init_patch = """        self.begin_time: float = 0

        # Predictive Thermal-Throttling state
        self._thermal_history = deque(maxlen=30)  # Stores (timestamp, temp)"""
content = content.replace("        self.begin_time: float = 0", init_patch)

# Replace _check_thermal_throttle
thermal_patch = """    def _check_thermal_throttle(self):
        \"\"\"
        Proactive Predictive Thermal-Throttling (AI-Driven).
        Forecasts thermal spikes before they hit the hardware limit using recent history.
        \"\"\"
        try:
            from pathlib import Path
            import time
            import numpy as np

            with Path("/sys/class/thermal/thermal_zone0/temp").open() as f:
                current_temp = float(f.read()) / 1000.0
                current_time = time.time()

                self._thermal_history.append((current_time, current_temp))

                # Reactive hard-throttle if already over 75C
                if current_temp > 75.0:
                    logger.warning(
                        f"[THERMAL THROTTLE] CPU at {current_temp:.1f}C. Pausing FreqAI for 15s."
                    )
                    time.sleep(15)
                    self._thermal_history.clear()
                    return

                # Predictive soft-throttle
                if len(self._thermal_history) > 5:
                    # Forecast horizon: 5 minutes (300 seconds)
                    times = np.array([t for t, _ in self._thermal_history])
                    temps = np.array([temp for _, temp in self._thermal_history])

                    # Normalize times for numerical stability
                    times_norm = times - times[0]

                    # Fit a 1st degree polynomial (linear regression)
                    if len(times_norm) > 1 and times_norm[-1] > 0:
                        slope, intercept = np.polyfit(times_norm, temps, 1)
                        predicted_temp = intercept + slope * (times_norm[-1] + 300) # + 5 min

                        if predicted_temp > 75.0 and slope > 0.05: # Rising at least 0.05C/sec
                            logger.warning(
                                f"[PREDICTIVE THROTTLE] CPU at {current_temp:.1f}C, but predicted to hit "
                                f"{predicted_temp:.1f}C in 5 min. Yielding execution for 10s."
                            )
                            time.sleep(10)
                            self._thermal_history.clear()
        except Exception as e:
            logger.debug(f"Predictive thermal check failed: {e}")"""

old_thermal = """    def _check_thermal_throttle(self):
        \"\"\"
        Checks CPU temperature on edge devices (like Raspberry Pi 5).
        If temp > 75C, sleep to prevent thermal throttling from affecting the trade loop.
        \"\"\"
        try:
            from pathlib import Path
            with Path("/sys/class/thermal/thermal_zone0/temp").open() as f:
                temp = float(f.read()) / 1000.0
                if temp > 75.0:
                    logger.warning(
                        f"[THERMAL THROTTLE] CPU at {temp:.1f}C. Pausing FreqAI training for 15s."
                    )
                    time.sleep(15)
        except Exception as e:
            logger.debug(f"Thermal check failed: {e}")"""

content = content.replace(old_thermal, thermal_patch)

with open('freqtrade/freqai/freqai_interface.py', 'w') as f:
    f.write(content)
