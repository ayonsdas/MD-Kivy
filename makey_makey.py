# Makey Makey detection - runs in the background and checks if one is plugged in
# Makey Makey shows up as a USB keyboard so we look for its vendor/product ID
# when connected the app shows the key legend and arrow keys start controlling the simulation

import threading
import os


# these are the USB vendor/product IDs for different versions of the Makey Makey / JoyLabz boards
# VID 1b4f = SparkFun Electronics (parent of JoyLabz / Makey Makey)
MAKEY_MAKEY_IDS = {
    ('1b4f', '2b74'),   # Classic v1.2
    ('1b4f', '2b75'),   # Classic v1.2 alternate
    ('1b4f', '2b96'),   # Go version
    ('1b4f', '2b97'),   # Go version alternate
    ('1b4f', '2b93'),   # Makey Max / newer variants
    ('1b4f', '2b94'),
    ('1b4f', '2b92'),
    ('1b4f', '2b76'),
}

# Fallback: if VID/PID is not in the list, match by product name containing these strings
MAKEY_MAKEY_PRODUCT_KEYWORDS = ('makey', 'makey makey', 'makeymakey', 'joylab')

# what each key does when Makey Makey is connected
# shown in the legend panel when its plugged in
# Covers: base board arrows, Player 2 D-pad (W/A/S/D/F/G), Makey Max keyboard section
KEY_LEGEND = [
    ('↑ / W / A',      'Gravity ▲'),
    ('↓ / S',          'Gravity ▼'),
    ('← / D',          'Epsilon ▼'),
    ('→',              'Epsilon ▲'),
    ('Space',          'Spawn molecule'),
    ('F',              'Sigma ▼'),
    ('G',              'Delta ▼'),
    ('Mouse click',    'Spawn molecule'),
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
        # also falls back to matching by product name (covers Makey Max and future variants)
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

                # Try to read the product name regardless — used for fallback matching
                prod_name = ''
                prod_path = os.path.join(usb_root, dev, 'product')
                if os.path.exists(prod_path):
                    with open(prod_path) as f:
                        prod_name = f.read().strip()

                # Match by VID/PID first, then by product name keyword
                vid_pid_match = (vid, pid) in MAKEY_MAKEY_IDS
                name_match = any(kw in prod_name.lower() for kw in MAKEY_MAKEY_PRODUCT_KEYWORDS)
                if vid_pid_match or name_match:
                    found = True
                    info  = prod_name or f'VID:{vid} PID:{pid}'
                    break
        except Exception:
            pass
        self.connected   = found
        self.device_info = info

    def stop(self):
        self._stop.set()
