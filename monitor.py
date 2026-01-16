import psutil
import time
import os

def monitor_usage(target):
    process = psutil.Popen(["python3", target], shell=True)
    while process.is_running():
        try:
            p = psutil.Process(process.pid)
            cpu_usage = p.cpu_percent(interval=1.0)
            mem_usage = p.memory_percent()
            print(f"CPU Usage: {cpu_usage:.2f}% | Memory Usage: {mem_usage}")
            time.sleep(1)
        except psutil.NoSuchProcess:
            break

if __name__ == "__main__":
    monitor_usage('main.py')