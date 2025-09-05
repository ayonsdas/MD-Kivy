import os
import re
import time
import socket
import serial
from serial.tools import list_ports

# This script reads data from an Arduino connected via serial port.

# Directly reading from the port ==> check connection!!!

# Plug in Arduino Test tHE port Later

#TO DO: Gravity Scale affects the ARDUINO
# One reading at a Time  ==> listening and transfering data through the serial port to collect data to python from C
class ArduinoReading:
    """Lightweight non-blocking reader for Arduino data over Serial or TCP (wireless).

    Features:
    - Serial mode: auto-detects a likely Arduino port if none is specified.
    - TCP mode: connects to an ESP/Arduino TCP server (e.g., ESP8266/ESP32 Wi‑Fi bridge).
    - Honors env vars: ARDUINO_MODE, ARDUINO_PORT, ARDUINO_BAUD, ARDUINO_TCP_HOST, ARDUINO_TCP_PORT.
    - Parses multiple formats, e.g. "X = 1 | Y = 2 | Z = 3" or "X: 1, Y: 2, Z: 3".
    - Returns None if no new complete line is available (non-blocking in UI loop).
    """

    def __init__(self, port=None, baud_rate=None, tcp_host=None, tcp_port=None, mode=None):
        # Env overrides
        env_mode = (os.getenv("ARDUINO_MODE") or '').lower().strip()
        env_port = os.getenv("ARDUINO_PORT")
        env_baud = os.getenv("ARDUINO_BAUD")
        env_tcp_host = os.getenv("ARDUINO_TCP_HOST")
        env_tcp_port = os.getenv("ARDUINO_TCP_PORT")

        # Determine transport
        self.mode = (mode or env_mode or '').lower() or ('tcp' if (tcp_host or env_tcp_host) else 'serial')

        # State
        self.serial_connection = None
        self.sock = None
        self._rx_buffer = b""
        self.last_xyz = None
        self.last_button = None  # 'HIGH'/'LOW'
        self.last_analog = None  # int

        # Regex patterns
        self._patterns = [
            re.compile(r"X\s*=\s*(-?\d+)\s*\|\s*Y\s*=\s*(-?\d+)\s*\|\s*Z\s*=\s*(-?\d+)"),
            re.compile(r"X\s*:\s*(-?\d+)\s*,\s*Y\s*:\s*(-?\d+)\s*,\s*Z\s*:\s*(-?\d+)")
        ]
        self._btn_pat = re.compile(r"\b(HIGH|LOW)\b", re.IGNORECASE)
        self._analog_pat = re.compile(r"\b(\d{1,5})\b")  # generic analog value

        if self.mode == 'tcp':
            # TCP mode (wireless)
            self.tcp_host = tcp_host or env_tcp_host or '192.168.4.1'
            self.tcp_port = int(tcp_port or (env_tcp_port or 8888))
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(3)
            self.sock.connect((self.tcp_host, self.tcp_port))
            self.sock.setblocking(False)
            self.port = f"tcp://{self.tcp_host}:{self.tcp_port}"
            self.baud_rate = None
            time.sleep(0.2)
        else:
            # Serial mode (default)
            self.port = port or env_port or self._auto_detect_port()
            self.baud_rate = int(baud_rate or (env_baud if env_baud else 9600))
            self.serial_connection = serial.Serial(self.port, self.baud_rate, timeout=0)
            time.sleep(2)

    @staticmethod
    def _auto_detect_port():
        """Pick a likely Arduino serial port on Linux.
        Looks for known VID/PID or ttyACM*/ttyUSB* names. Returns a string or default '/dev/ttyACM0'.
        """
        candidates = []
        try:
            for p in list_ports.comports():
                name = p.device or ""
                desc = (p.description or "").lower()
                hwid = (p.hwid or "").lower()
                if any(k in desc for k in ["arduino", "ch340", "usb serial", "cp210", "ttyacm", "ttyusb"]) or \
                   any(k in name for k in ["ttyacm", "ttyusb"]) or \
                   any(k in hwid for k in ["2341:", "1a86:", "10c4:"]):
                    candidates.append(name)
        except Exception:
            pass

        if candidates:
            return candidates[0]
        # Reasonable Linux default for Arduino-class devices
        return "/dev/ttyACM0"

    def _parse_xyz_line(self, line: str):
        for pat in self._patterns:
            m = pat.search(line)
            if m:
                x, y, z = map(int, m.groups())
                return x, y, z
        return None

    def _readline_nonblocking(self):
        """Return one line as bytes (without newline) if available; else None."""
        if self.serial_connection:
            try:
                if self.serial_connection.in_waiting:
                    raw = self.serial_connection.readline()
                    return raw.rstrip(b"\r\n") if raw else None
            except Exception:
                return None
            return None
        elif self.sock:
            try:
                chunk = self.sock.recv(4096)
                if chunk:
                    self._rx_buffer += chunk
            except (BlockingIOError, TimeoutError):
                pass
            except Exception:
                return None
            if b"\n" in self._rx_buffer:
                line, _, rest = self._rx_buffer.partition(b"\n")
                self._rx_buffer = rest
                return line.rstrip(b"\r")
            return None
        return None

    def _consume_and_parse(self):
        raw = self._readline_nonblocking()
        if not raw:
            return False
        try:
            line = raw.decode('utf-8', errors='ignore').strip()
        except Exception:
            return False

        # Parse XYZ
        xyz = self._parse_xyz_line(line)
        if xyz:
            self.last_xyz = xyz

        # Parse HIGH/LOW
        m = self._btn_pat.search(line)
        if m:
            self.last_button = m.group(1).upper()

        # Parse analog value (heuristic)
        m2 = self._analog_pat.search(line)
        if m2:
            try:
                val = int(m2.group(1))
                if 0 <= val <= 65535:
                    self.last_analog = val
            except Exception:
                pass
        return True

    def get_xyz(self):
        """Return (x, y, z) if new data is available; else None. Non-blocking."""
        try:
            if self._consume_and_parse() and self.last_xyz is not None:
                return self.last_xyz
        except Exception:
            return None
        return None

    def get_button_state(self):
        """Return 'HIGH'/'LOW' if present; else None."""
        self._consume_and_parse()
        return self.last_button

    def get_analog(self):
        """Return last analog reading if present; else None."""
        self._consume_and_parse()
        return self.last_analog

    @property
    def connection_info(self):
        if self.sock:
            return f"tcp://{getattr(self, 'tcp_host', '?')}:{getattr(self, 'tcp_port', '?')}"
        return f"{self.port} @ {self.baud_rate}"

    def close(self):
        try:
            if self.serial_connection and self.serial_connection.is_open:
                self.serial_connection.close()
        except Exception:
            pass
        try:
            if self.sock:
                self.sock.close()
        except Exception:
            pass
    

    # WHen wreless thing is going to be done than do it
    # take this part of code to fentch extra info about HIGH and LOW and Senosr for rotation 
# Possibility !!!!
# Code from C !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
#     void  loop(){
#   int sensorValue = analogRead(A0);
#   // print out the value you read:
#   Serial.println(sensorValue);
#   delay(1);  // delay in between reads for stability
  
#   // read the state of the pushbutton value:
#   buttonState = digitalRead(buttonPin);

#   // check if the pushbutton is pressed. If it is, the buttonState is HIGH:
#   if (buttonState == HIGH) {
#     // turn LED on:
#     Serial.println("HIGH");
#   } else {
#     // turn LED off:
#     Serial.println("LOW");
#   }
  
    


    # def __init__(self, port='/dev/ttyACM0', baud_rate=9600):
    #     self.port = port
    #     self.baud_rate = baud_rate
    #     self.serial_connection = serial.Serial(self.port, self.baud_rate)
    #     time.sleep(2)  # waiting for the Arduino to reset

    # def read_data(self):
    #     try:
    #         while True:
    #             line = self.serial_connection.readline().decode('utf-8').strip()
    #             print("Raw line:", line)

    #             match = re.search(r'X\s*=\s*(-?\d+)\s*\|\s*Y\s*=\s*(-?\d+)\s*\|\s*Z\s*=\s*(-?\d+)', line)
    #             if match:
    #                 x, y, z = map(int, match.groups())
    #                 print(f"X: {x}, Y: {y}, Z: {z}")
    #             else:
    #                 print("No match found in the line")
    #     except KeyboardInterrupt:
    #         print("Stopping Script.")
    #     finally:
    #         self.serial_connection.close()
    #         print("Serial connection closed.")





# First Idea:      
# arduino_port  = '/dev/ttyACMO'
# baud_rate = 9600

# serial_connection = serial.Serial(arduino_port, baud_rate)
# time.sleep(2)  # waiting for the connection to establish

# print("Connected to Arduino on port - reading data")
# try: 
#     while True: 
#         line = serial_connection.readline().decode('utf-8').strip()
#         print("row line", line)
#         # Parce the accelerometer data
#         match = re.match(r'X: (-?\d+), Y: (-?\d+), Z: (-?\d+)', line)
#         if match:
#             x, y, z = map(int, match.groups())
#             print(f"X: {x}, Y: {y}, Z: {z}")
#         else:
#             print("No match found in the line")
# except KeyboardInterrupt:
#     print(f"Stopping SCript:")
# finally:
#     serial_connection.close()
#     print("Serial connection closed")
            



