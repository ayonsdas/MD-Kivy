# --- performance_monitor.py ---
import psutil
import threading
import time
import collections
from datetime import datetime

class PerformanceMonitor:
    def __init__(self, sample_interval=0.2):
        self.sample_interval = sample_interval
        self.process = psutil.Process()
        self.cpu_history = collections.deque(maxlen=30) # changes from 10 to 30 to make less carzy
        self.cpu_usage = 0.0

        self.boost = 0.0
        self.last_boost = time.time()

        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def _monitor_loop(self):
        while True:
            raw_cpu = self.process.cpu_percent(interval=None)
            
            # decay boost
            now = time.time()
            delta = now - self.last_boost
            self.boost = max(0, self.boost - 5 * delta)
            self.last_boost = now

            usage = raw_cpu + self.boost
            self.cpu_history.append(min(usage, 100))
            self.cpu_usage = sum(self.cpu_history) / len(self.cpu_history)

            time.sleep(self.sample_interval)

    def get_cpu_usage(self):
        return round(self.cpu_usage, 1)

    def trigger_boost(self, amount=15):
        self.boost += amount
        self.last_boost = time.time()

    def update_simulation_metrics(self, molecule_count, gravity, epsilon, speed):
        activity = molecule_count * 0.4 + gravity * 2 + epsilon * 2 + speed * 10
        self.trigger_boost(activity)


# optional global access
_global_monitor = None

def set_global_monitor(monitor):
    global _global_monitor
    _global_monitor = monitor

def get_global_monitor():
    return _global_monitor
