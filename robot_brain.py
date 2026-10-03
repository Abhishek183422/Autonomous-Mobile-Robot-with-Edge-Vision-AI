import serial
import time
import requests
import threading
import queue
from picamera2 import Picamera2

# --- 1. SETUP CAMERA ---
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(camera_config)
picam2.start()
time.sleep(1)

# --- 2. SETUP ARDUINO ---
# MAKE SURE THIS MATCHES YOUR ARDUINO PORT! (/dev/ttyACM0 or /dev/ttyUSB0)
arduino = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2)

# --- 3. SETUP MAC BRAIN ---
# MAKE SURE THIS MATCHES YOUR MAC'S IP ADDRESS!
MAC_IP = "192.168.0.118" 
BRAIN_URL = f"http://{MAC_IP}:5000/think"

# --- 4. THE QUEUE (Shared memory between threads) ---
command_queue = queue.Queue()

def capture_image():
    image_path = "/tmp/pi_photo.jpg"
    picam2.capture_file(image_path)
    return image_path

def ask_brain_for_direction(image_path):
    try:
        with open(image_path, 'rb') as img:
            files = {'image': img}
            response = requests.post(BRAIN_URL, files=files, timeout=20)
            
        if response.status_code == 200:
            data = response.json()
            command = data['command']
            print(f"🧠 Brain decided: {command}")
            return command
        else:
            print("Error from brain server:", response.text)
            return "STOP"
    except Exception as e:
        print(f"Failed to reach brain: {e}")
        return "STOP"

def send_to_arduino(cmd_letter):
    arduino.write(cmd_letter.encode('utf-8'))

# --- THREAD 1: THE THINKER ---
def brain_thread_func():
    print("🧠 Brain thread started.")
    while True:
        photo = capture_image()
        time.sleep(0.5)
        decision = ask_brain_for_direction(photo)
        
        # Translate word to letter for Arduino
        if decision == "FORWARD":
            command_queue.put('F')
        elif decision == "LEFT":
            command_queue.put('L')
        elif decision == "RIGHT":
            command_queue.put('R')
        else:
            command_queue.put('S')
            
        time.sleep(1) # Small breather before taking next photo

# --- THREAD 2: THE DRIVER ---
def driver_thread_func():
    print("🚗 Driver thread started.")
    while True:
        # Check if the Brain put a new command in the queue
        if not command_queue.empty():
            cmd = command_queue.get()
            
            # Execute the special action
            if cmd in ['F', 'L', 'R']:
                send_to_arduino(cmd)
                time.sleep(1.5) # Let the Arduino finish the boost/turn
            else:
                send_to_arduino(cmd) # STOP
                
        else:
            # No new command? Keep creeping forward!
            send_to_arduino('C')
            time.sleep(0.2) # Send creep command 5 times a second

# --- START THE SYSTEM ---
if __name__ == '__main__':
    print("Starting Parallel Autonomous System...")
    
    # Create the threads
    brain_thread = threading.Thread(target=brain_thread_func)
    driver_thread = threading.Thread(target=driver_thread_func)
    
    # Start them
    brain_thread.start()
    driver_thread.start()
    
    # Keep main script alive
    brain_thread.join()
    driver_thread.join()
