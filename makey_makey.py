# Makey Makey detection - runs in the background and checks if one is plugged in
# Makey Makey shows up as a USB keyboard so we look for its vendor/product ID
# when connected the app shows the key legend and arrow keys start controlling the simulation

import threading
import os


# these are the USB vendor/product IDs for different versions of the Makey Makey
MAKEY_MAKEY_IDS = {
    ('1b4f', '2b74'),   # Classic v1.2
    ('1b4f', '2b75'),   # Classic v1.2 alternate
    ('1b4f', '2b96'),   # Go version
    ('1b4f', '2b97'),
}

# what each key does when Makey Makey is connected
# shown in the legend panel when its plugged in
KEY_LEGEND = [
    ('↑  Up Arrow',    'Gravity ▲'),
    ('↓  Down Arrow',  'Gravity ▼'),
    ('←  Left Arrow',  'Epsilon ▼'),
    ('→  Right Arrow', 'Epsilon ▲'),
    ('Space',          'Spawn molecule'),
    ('W / S',          'Gravity fine tune'),
]


class MakeyMakeyMonitor:
    # polls the USB device list every 2 seconds in a background thread
    # just read .connected and .device_info from the main thread, they update automatically

    def __init__(self, poll_interval: float = 2.0):
        self.connected   = False
        self.device_info = ''
        self._interval   = poll_interval
        self._stop       = threading.Event()
        self._thread     = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while not self._stop.wait(self._interval):
            self._check()

    def _check(self):
        # scan the usb device folder and look for a matching vendor/product ID
        usb_root = '/sys/bus/usb/devices'
        if not os.path.isdir(usb_root):
            return
        found = False
        info  = ''
        try:
            for dev in os.listdir(usb_root):
                vid_path = os.path.join(usb_root, dev, 'idVendor')
                pid_path = os.path.join(usb_root, dev, 'idProduct')
                if not (os.path.exists(vid_path) and os.path.exists(pid_path)):
                    continue
                with open(vid_path) as f:
                    vid = f.read().strip()
                with open(pid_path) as f:
                    pid = f.read().strip()
                if (vid, pid) in MAKEY_MAKEY_IDS:
                    found = True
                    # try to get the product name for the status label
                    prod_path = os.path.join(usb_root, dev, 'product')
                    if os.path.exists(prod_path):
                        with open(prod_path) as f:
                            info = f.read().strip()
                    else:
                        info = f'VID:{vid} PID:{pid}'
                    break
        except Exception:
            pass
        self.connected   = found
        self.device_info = info

    def stop(self):
        self._stop.set()
