import psutil
import threading
import time
import collections

class PerformanceMonitor:
    def __init__(self, sample_interval=0.2):
        self.sample_interval = sample_interval
        self.process = psutil.Process()
        self.cpu_history = collections.deque(maxlen=30)
        self.cpu_usage = 0.0
        self.simulation_load = 0.0  # This will hold the live activity level

        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def _monitor_loop(self):
        while True:
            # Simulate work proportional to simulation load (burn CPU)
            for _ in range(int(self.simulation_load)):
                _ = sum(i * i for i in range(30))  # Adjust as needed

            # Measure actual CPU usage
            raw_cpu = self.process.cpu_percent(interval=self.sample_interval)

            self.cpu_history.append(min(raw_cpu, 100))
            self.cpu_usage = sum(self.cpu_history) / len(self.cpu_history)

    def get_cpu_usage(self):
        return round(self.cpu_usage, 1)

    def update_simulation_metrics(self, molecule_count, gravity, epsilon, speed, forces_on):
        # Scale the activity more smartly
        force_multiplier = 2 if forces_on else 0.1
        activity_score = (molecule_count ** 0.9) * gravity * epsilon * speed * force_multiplier
        self.simulation_load = activity_score  # This is now live and smooth



# optional global access
_global_monitor = None

def set_global_monitor(monitor):
    global _global_monitor
    _global_monitor = monitor

def get_global_monitor():
    return _global_monitor
