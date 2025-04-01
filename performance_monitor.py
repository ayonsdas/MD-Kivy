import psutil
import threading
import time
import collections

class PerformanceMonitor:
    def __init__(self, sample_interval=1.0):
        """
        Initializes the PerformanceMonitor with a sample interval in seconds.
        This creates and starts a background thread to measure CPU and memory usage.
        """
        self.sample_interval = sample_interval
        self.running = True

        self.process = psutil.Process()

        # CPU usage variables
        self.cpu_usage = 0.0
        self.cpu_history = collections.deque(maxlen=5)  # smoothing over last 5 samples

        # Memory usage variables (system-wide in this example)
        self.memory_usage = 0.0
        self.memory_history = collections.deque(maxlen=5)

        self.thread = threading.Thread(target=self._update_usage, daemon=True)
        self.thread.start()

    def _update_usage(self):
        """
        Continuously update CPU and memory usage for this Python process (CPU)
        and the entire system (memory). The loop ends when self.running is False.
        """
        while self.running:
            try:
                # Measure CPU usage for this process
                raw_cpu = self.process.cpu_percent(interval=0.3)
                self.cpu_history.append(raw_cpu)
                self.cpu_usage = sum(self.cpu_history) / len(self.cpu_history)

                # Measure system memory usage:
                raw_mem = psutil.virtual_memory().percent
                self.memory_history.append(raw_mem)
                self.memory_usage = sum(self.memory_history) / len(self.memory_history)

                print(f"[DEBUG] CPU raw={raw_cpu:.2f}% smoothed={self.cpu_usage:.2f}%, "
                      f"Mem raw={raw_mem:.2f}% smoothed={self.memory_usage:.2f}%")

            except Exception as e:
                print(f"Error measuring usage: {e}")

            # Sleep for your chosen sample interval before measuring again
            time.sleep(self.sample_interval)

    def stop(self):
        """
        Stop the monitoring loop by setting self.running to False"""
        self.running = False
        if self.thread.is_alive():
            self.thread.join()

    def get_cpu_usage(self):
        """
        Returns the current smoothed CPU usage of *this* Python process (0-100+%).
        On multi-core systems, usage can exceed 100% if multiple cores are used.
        """
        return round(self.cpu_usage, 2)

    def get_memory_usage(self):
        return round(self.memory_usage, 2)
    

# class PerformanceMonitor:
#     def __init__(self, sample_interval=0.5):
#         self.sample_interval = sample_interval
#         self.running = True
#         self.process = psutil.Process()

#         self.cpu_usage = 0.0
#         self.cpu_history = collections.deque(maxlen=10)

#         self.memory_usage = 0.0
#         self.memory_history = collections.deque(maxlen=10)

#         # For artificial boost logic
#         self.artificial_boost = 0.0
#         self.last_boost_time = datetime.min

#         self.thread = threading.Thread(target=self._update_usage, daemon=True)
#         self.thread.start()

#     def _update_usage(self):
#         while self.running:
#             try:
#                 # Get base CPU usage (adjusted for number of cores)
#                 base_cpu = self.process.cpu_percent(interval=None) / psutil.cpu_count()

#                 # Handle decay of artificial boost
#                 seconds_since_boost = (datetime.now() - self.last_boost_time).total_seconds()
#                 decay_rate = 10.0  # how fast the boost fades per second
#                 self.artificial_boost = max(0, self.artificial_boost - decay_rate * seconds_since_boost)
#                 self.last_boost_time = datetime.now()

#                 # Combine real CPU with artificial boost
#                 combined_cpu = base_cpu + self.artificial_boost
#                 self.cpu_history.append(combined_cpu)
#                 self.cpu_usage = sum(self.cpu_history) / len(self.cpu_history)

#                 # Memory stays real only
#                 raw_mem = psutil.virtual_memory().percent
#                 self.memory_history.append(raw_mem)
#                 self.memory_usage = sum(self.memory_history) / len(self.memory_history)

#                 print(f"[DEBUG] CPU base={base_cpu:.2f}% + boost={self.artificial_boost:.2f}%, "
#                       f"final={self.cpu_usage:.2f}%, Mem={self.memory_usage:.2f}%")

#             except Exception as e:
#                 print(f"[ERROR] {e}")
#             time.sleep(self.sample_interval)

#     def stop(self):
#         self.running = False
#         if self.thread.is_alive():
#             self.thread.join()

#     def get_cpu_usage(self):
#         return round(self.cpu_usage, 2)

#     def get_memory_usage(self):
#         return round(self.memory_usage, 2)

#     def trigger_boost(self, magnitude=25.0):
#         """
#         Call this when the user does something significant like:
#         - Adding molecules
#         - Toggling forces
#         - Increasing sliders
#         """
#         self.artificial_boost += magnitude
#         self.last_boost_time = datetime.now()

