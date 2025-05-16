import serial
import time
import re

# This script reads data from an Arduino connected via serial port.

# Directly reading from the port ==> check connection!!!

# Plug in Arduino Test tHE port Later

#TO DO: Gravity Scale affects the ARDUINO
# One reading at a Time  ==> listening and transfering data through the serial port to collect data to python from C++
class ArduinoReading:
    def __init__(self, port='/dev/ttyUSB0', baud_rate=9600):
        self.serial_connection = serial.Serial(port, baud_rate)
        time.sleep(2)

    def get_xyz(self):
        while self.serial_connection.in_waiting:
            try:
                line = self.serial_connection.readline().decode('utf-8').strip()
                match = re.search(r'X\s*=\s*(-?\d+)\s*\|\s*Y\s*=\s*(-?\d+)\s*\|\s*Z\s*=\s*(-?\d+)', line)
                if match:
                    return map(int, match.groups())
            except Exception as e:
                print("Read error:", e)
        return None  # No new data
    


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
            



