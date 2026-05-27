import serial
import time
import threading
from datetime import datetime
import os

port = "/dev/cu.usbserial-110"
baud = 115200

stop_recording = False

def read_and_record(ser, output_file):
    global stop_recording
    try:
        with open(output_file, 'w') as f:
            while not stop_recording:
                try:
                    line = ser.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        timestamp = time.time()
                        f.write(f"{timestamp},{line}\n")
                        f.flush()  
                except Exception as e:
                    print(f"Error reading/decoding line: {e}")
    except Exception as e:
        print(f"File writing error: {e}")

def start_recording():
    global stop_recording
    os.makedirs("testsets", exist_ok=True)
    os.makedirs("testsets/unnamed", exist_ok=True)
    try:
        ser = serial.Serial(port, baud, timeout=1.0)
    except serial.SerialException as e:
        print(f"Failed to open serial port {port}: {e}")
        return

    time.sleep(2)
    if ser.in_waiting > 0:
        ser.reset_input_buffer()

    default_filename = f"testsets/unnamed/serial_record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    filename_input = input(f"Enter output filename (default: {default_filename}): ")
    output_file = filename_input.strip() if filename_input.strip() else default_filename

    print(f"\nRecording to '{output_file}'...")
    print("Press Enter to stop recording.\n")

    recording_thread = threading.Thread(target=read_and_record, args=(ser, output_file), daemon=True)
    recording_thread.start()

    input()
    
    print("Stopping recording...")
    stop_recording = True

    recording_thread.join(timeout=2.0)
    ser.close()
    print("Done.")

if __name__ == "__main__":
    start_recording()
