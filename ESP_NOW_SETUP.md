# ESP-NOW Wireless Arduino Setup Guide

## What You Have

You have two ESP32 boards:
1. **Transmitter**: ESP32 + MPU6050 accelerometer (wireless, battery-powered)
2. **Receiver**: ESP32 connected to your computer via USB

They communicate wirelessly using ESP-NOW protocol.

---

## Step-by-Step Setup

### Step 1: Get the Receiver's MAC Address

1. **Connect the RECEIVER ESP32** to your computer via USB
2. **Open Arduino IDE**
3. **Flash this simple code** to find its MAC address:

```cpp
#include <WiFi.h>

void setup() {
  Serial.begin(9600);
  WiFi.mode(WIFI_STA);
  Serial.print("Receiver MAC Address: ");
  Serial.println(WiFi.macAddress());
}

void loop() {
  delay(1000);
}
```

4. **Open Serial Monitor** (115200 baud)
5. **Copy the MAC address** (looks like: `AA:BB:CC:DD:EE:FF`)

### Step 2: Update Transmitter Code

1. **Open `arduino_transmitter_fixed.ino`** (in your MD-Kivy folder)
2. **Find this line:**
   ```cpp
   uint8_t broadcastAddress[] = {0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF};
   ```
3. **Replace with your receiver's MAC address:**
   
   If MAC is `AA:BB:CC:DD:EE:FF`, change it to:
   ```cpp
   uint8_t broadcastAddress[] = {0xAA, 0xBB, 0xCC, 0xDD, 0xEE, 0xFF};
   ```
   
   Example: If MAC is `24:6F:28:A1:B2:C3`:
   ```cpp
   uint8_t broadcastAddress[] = {0x24, 0x6F, 0x28, 0xA1, 0xB2, 0xC3};
   ```

### Step 3: Flash the Transmitter

1. **Connect TRANSMITTER ESP32** (the one with MPU6050) to computer
2. **Open `arduino_transmitter_fixed.ino`** in Arduino IDE
3. **Select board**: Tools → Board → ESP32 Arduino → ESP32 Dev Module
4. **Select port**: Tools → Port → (your ESP32 port)
5. **Upload the code**
6. **Disconnect and power with battery** (or leave on USB for testing)

### Step 4: Flash the Receiver

1. **Connect RECEIVER ESP32** to computer
2. **Open `arduino_receiver_fixed.ino`** in Arduino IDE
3. **Select board and port** (same as before)
4. **Upload the code**
5. **Keep connected to USB** (this one stays connected to your computer)

### Step 5: Test the Connection

1. **Open Serial Monitor** (9600 baud) with receiver connected
2. **Move/shake the transmitter** (the one with MPU6050)
3. **You should see:**
   ```
   X = 1234 | Y = 5678 | Z = 9012
   X = 1245 | Y = 5690 | Z = 9025
   ...
   ```

If you see this, **SUCCESS!** The wireless connection works.

### Step 6: Run the Python App

Now the receiver is sending data in the correct format. Run your app:

**Linux/Mac:**
```bash
cd ~/Final_Molecular_Project/MD-Kivy
source vislab_env/bin/activate
./run_wired.sh
```

**Windows:**
1. Edit `run_wired.bat` to set your COM port
2. Double-click `run_wired.bat`

Or just run normally:
```bash
python main.py
```

The app will auto-detect the Arduino on USB and start receiving wireless accelerometer data!

---

## How It Works

```
[Transmitter ESP32]           [Receiver ESP32]          [Your Computer]
  + MPU6050        --ESP-NOW-->  (wireless)    --USB-->   Python App
  (wireless)          |                                      |
                      |                                      |
     Shake/Move ------+----------> Serial Data ---------> Affects Molecules!
```

1. **Transmitter** reads MPU6050 accelerometer
2. **Sends data wirelessly** via ESP-NOW to receiver
3. **Receiver** gets data and sends to computer via USB serial
4. **Python app** reads serial data and affects molecular simulation

---

## Troubleshooting

### Transmitter shows "Delivery Fail"

**Problem:** Wrong MAC address or receiver not powered

**Solution:**
- Double-check MAC address in transmitter code
- Make sure receiver is powered and running
- Boards should be within 10-20 meters

### No data in Serial Monitor

**Problem:** Boards not communicating

**Solution:**
1. Check both boards are flashed correctly
2. Restart both ESP32 boards
3. Verify MAC address is correct
4. Try broadcasting: Use `{0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF}` for testing

### Python app not reading data

**Problem:** Wrong serial port or baud rate

**Solution:**
- Check Device Manager (Windows) or `ls /dev/tty*` (Linux) for port
- Make sure receiver Serial.begin is set to **9600** (not 115200)
- Update port in `run_wired.sh` or `run_wired.bat`

### Data format wrong

**Problem:** Python app can't parse data

**Solution:**
- Receiver MUST print in format: `X = 1234 | Y = 5678 | Z = 9012`
- Check receiver code has the modified Serial.print statements
- Test with Serial Monitor first before running Python app

---

## Configuration Summary

### Transmitter (Wireless ESP32 + MPU6050):
- **Baud Rate:** 115200 (for debugging only)
- **MAC Address:** Set to receiver's MAC
- **Send Interval:** Every 100ms
- **Power:** Battery or USB (can be wireless)

### Receiver (USB-Connected ESP32):
- **Baud Rate:** 9600 (MUST match Python app default)
- **Connection:** USB to computer
- **Output Format:** `X = value | Y = value | Z = value`
- **Mode:** Wi-Fi Station for ESP-NOW

### Python App:
- **Default Baud:** 9600
- **Auto-detect:** Finds Arduino on /dev/ttyACM0, /dev/ttyUSB0, COM3, etc.
- **Data Format:** Parses `X = value | Y = value | Z = value`

---

## Quick Test Commands

### Get receiver MAC address:
```cpp
Serial.println(WiFi.macAddress());
```

### Test data format manually:
Open Serial Monitor and type:
```
X = 1000 | Y = 2000 | Z = 3000
```
Python app should recognize this format.

### Check if Python sees Arduino:
```bash
# Linux
ls /dev/ttyACM* /dev/ttyUSB*

# Windows - Device Manager
devmgmt.msc
```

---

## Files You Need

- ✅ `arduino_transmitter_fixed.ino` - Flash to transmitter ESP32
- ✅ `arduino_receiver_fixed.ino` - Flash to receiver ESP32
- ✅ `run_wired.sh` / `run_wired.bat` - Launch script for Python app
- ✅ `arduino_reading.py` - Already supports this format!

---

**You're all set! Shake the transmitter and watch molecules react!** 🚀
