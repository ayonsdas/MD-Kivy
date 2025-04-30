import psutil
import threading
import time
import collections
from datetime import datetime



# TO DO: ==> limit the size to two digits and clean using teh stuff below
# Determine what nums ==> num molecules and sum them mun of computation that sould be happening if forces on and not one
# Clarify of foces to avtual output compare or affect teh output?
# More molecules increase performance
# Smaller graohs ggod to make
# 

class PerformanceMonitor:
    def __init__(self, sample_interval=0.5):
        self.sample_interval = sample_interval
        self.running = True
        self.process = psutil.Process()

        self.cpu_usage = 0.0
        self.cpu_history = collections.deque(maxlen=10)

        self.memory_usage = 0.0
        self.memory_history = collections.deque(maxlen=10)

        # Boost logic
        self.artificial_boost = 0.0
        self.last_boost_time = datetime.now()

        self.thread = threading.Thread(target=self._update_usage, daemon=True)
        self.thread.start()

    def _update_usage(self):
        while self.running:
            try:
                base_cpu = self.process.cpu_percent(interval=None) / psutil.cpu_count()

                now = datetime.now()
                seconds_since_boost = (now - self.last_boost_time).total_seconds()
                decay_rate = 10.0
                self.artificial_boost = max(0, self.artificial_boost - decay_rate * seconds_since_boost)
                self.last_boost_time = now

                combined_cpu = base_cpu + self.artificial_boost
                self.cpu_history.append(combined_cpu)  # cpu his self.pop.left(0)   <== take it  ==> push_right for append?? ==> for adding to clean teh histroy
                self.cpu_usage = sum(self.cpu_history) / len(self.cpu_history) # how large list be ==? remove form the left
                    # contol size fo teh CPU HIstory ==> use above 
                # Memory logic
                raw_mem = psutil.virtual_memory().percent
                self.memory_history.append(raw_mem)
                self.memory_usage = sum(self.memory_history) / len(self.memory_history)

                print(f"[DEBUG] CPU base={base_cpu:.2f}% + boost={self.artificial_boost:.2f}%, "
                      f"final={self.cpu_usage:.2f}%, Mem={self.memory_usage:.2f}%")

            except Exception as e:
                print(f"[ERROR] {e}")

            time.sleep(self.sample_interval)

    def trigger_boost(self, amount=25.0):
        self.artificial_boost += amount
        self.last_boost_time = datetime.now()

    def get_cpu_usage(self):
        return round(self.cpu_usage, 2)

    def update_simulation_metrics(self, molecule_count, gravity, epsilon, speed):
        activity_score = molecule_count * 0.5 + gravity * 5 + epsilon * 3 + speed * 10
        self.trigger_boost(activity_score)

# --- Global Access Pattern ---
_global_monitor = None

def set_global_monitor(monitor):
    global _global_monitor
    _global_monitor = monitor

def get_global_monitor():
    return _global_monitor


# len of molecules collected properly!!!!