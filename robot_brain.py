import serial
import time
import requests
import threading
import queue
from picamera2 import Picamera2


# Camera setup
picam2 = Picamera2()
camera_config = picam2.create_preview_configuration(
    main={"size": (640, 480)}
)
picam2.configure(camera_config)
picam2.start()

time.sleep(1)


# Arduino connection
arduino = serial.Serial("/dev/ttyACM0", 9600, timeout=1)
time.sleep(2)


# Mac server
MAC_IP = "192.168.0.118"
BRAIN_URL = f"http://{MAC_IP}:5000/think"


# Used to pass commands from the brain thread to the driver thread
command_queue = queue.Queue()


def capture_image():
    image_path = "/tmp/pi_photo.jpg"

    picam2.capture_file(image_path)

    return image_path


def ask_brain(image_path):
    try:
        with open(image_path, "rb") as image:
            response = requests.post(
                BRAIN_URL,
                files={"image": image},
                timeout=20
            )

        if response.status_code == 200:
            data = response.json()
            command = data["command"]

            print("Brain:", command)

            return command

        print("Brain error:", response.text)
        return "STOP"

    except Exception as e:
        print("Could not connect :", e)
        return "STOP"


def send_command(command):
    arduino.write(command.encode("utf-8"))


def brain_thread():
    print("brain thread started")

    while True:
        image = capture_image()

        time.sleep(0.5)

        decision = ask_brain(image)

        # Convert the brain's response to the command
        # expected by the Arduino.
        if decision == "FORWARD":
            command_queue.put("F")

        elif decision == "LEFT":
            command_queue.put("L")

        elif decision == "RIGHT":
            command_queue.put("R")

        else:
            command_queue.put("S")

        time.sleep(1)


def driver_thread():
    print("driving thread started")

    while True:
        if not command_queue.empty():
            command = command_queue.get()

            if command in ["F", "L", "R"]:
                send_command(command)

                print("Arduino:", command)

                # Give the Arduino some time to complete the movement
                time.sleep(1.5)

            else:
                send_command("S")
                print("Arduino: STOP")

        else:
            # Nothing from the brain yet, so keep the robot moving slowly.
            send_command("C")
            time.sleep(0.2)


if __name__ == "__main__":
    print("Starting....")

    brain_thread = threading.Thread(target=brain_thread)
    driver_thread = threading.Thread(target=driver_thread)

    brain_thread.start()
    driver_thread.start()

    brain_thread.join()
    driver_thread.join()
