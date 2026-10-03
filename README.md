# Autonomous Mobile Robot with Edge Vision AI

A Phase 1 proof-of-concept autonomous mobile robot built using a Raspberry Pi, Arduino, camera, ToF distance sensor, and a locally running Vision-Language Model.

The main goal of this project was to experiment with using AI for high-level navigation while keeping the actual motor control and basic obstacle safety on a microcontroller.

## Demo

**Demo video:** [Add your YouTube/video link here]

The video shows the robot receiving visual input, sending the image to the AI system, receiving a navigation command, and controlling the motors through the Arduino.

---

## Hardware

* Raspberry Pi 4
* 5MP CSI Camera
* Arduino Uno
* VL53L0X ToF distance sensor
* DC motors
* H-bridge motor driver
* 2S2P lithium battery setup
* 5V buck converter

---

## How It Works

The system is split between the Raspberry Pi and Arduino.

The Raspberry Pi handles the camera and communicates with a locally running Vision-Language Model. The model looks at the camera image and returns a simple navigation command:

```text
FORWARD
LEFT
RIGHT
STOP
```

The Raspberry Pi then converts these commands into simple serial commands and sends them to the Arduino.

The Arduino controls the motors and continuously checks the VL53L0X distance sensor.

The basic flow is:

```text
Camera
   ↓
Raspberry Pi
   ↓
Vision-Language Model
   ↓
FORWARD / LEFT / RIGHT / STOP
   ↓
Arduino
   ↓
Motor Driver
   ↓
Motors
```

At the same time:

```text
VL53L0X
   ↓
Arduino
   ↓
Obstacle detected
   ↓
Stop motors
```

This means the Arduino can stop the robot when an obstacle gets too close, even if the AI system is still processing an image.

---

## Software

### Raspberry Pi

The Raspberry Pi runs a Python program that:

* Captures images from the camera
* Sends images to the AI server
* Receives the navigation decision
* Converts the decision into a simple motor command
* Sends commands to the Arduino over serial

The AI processing runs in a separate thread so that the robot does not have to completely stop while waiting for the next AI response.

A Python queue is used to pass commands between the AI thread and the motor-control thread.

Example:

```text
AI response
    ↓
Command Queue
    ↓
Driver Thread
    ↓
Arduino
```

### Arduino

The Arduino is responsible for the low-level control.

It:

* Receives commands from the Raspberry Pi
* Controls the motor driver
* Reads the VL53L0X sensor
* Stops the motors when an obstacle is detected within the configured safety distance
* Allows turning commands when the forward path is blocked

The current safety distance is:

```text
300 mm / 30 cm
```

---

## Handling AI Latency

One of the main problems I wanted to solve was AI inference latency.

A Vision-Language Model can take a few seconds to process an image. If the robot simply waited for every response, the movement would look very slow and inconsistent.

To handle this, the Raspberry Pi uses two threads:

### Brain thread

Captures an image and sends it to the AI system.

```text
Camera → AI → Navigation command
```

### Driver thread

Continuously handles the latest available motor command and communicates with the Arduino.

When there is no new AI command, the robot can use a slow creep command instead of completely stopping.

This keeps the robot moving while the next AI decision is being processed.

---

## Safety Handling

The AI is not responsible for the final emergency stop.

The Arduino continuously checks the VL53L0X sensor.

If an object is detected within 30 cm:

```text
Obstacle detected
       ↓
Arduino stops motors
       ↓
Forward commands are ignored
       ↓
Turning commands can still be used
```

This provides a basic hardware-level safety layer independent of the AI response.

---

## Power System

The prototype uses a 7.4V battery setup for the motor/actuator side.

A buck converter is used to provide the required lower voltage for the electronics.

The basic power arrangement is:

```text
Battery
   ├── Motor Driver → Motors
   │
   └── Buck Converter → 5V Electronics
                         ├── Raspberry Pi
                         ├── Arduino
                         └── Sensors
```

The purpose of separating the motor and logic power paths is to reduce the effect of motor-related electrical noise on the electronics.

---

## Repository Structure

```text
autonomous-mobile-robot/
│
├── raspberry_pi/
│   └── robot.py
│
├── arduino/
│   └── robot_controller.ino
│
├── images/
│   └── robot.jpg
│
├── videos/
│   └── demo.mp4
│
└── README.md
```

---

## Current Status

### Phase 1 — Completed

* Raspberry Pi camera integration
* Raspberry Pi → AI communication
* AI-based navigation commands
* Raspberry Pi → Arduino serial communication
* Arduino motor control
* VL53L0X obstacle detection
* Basic emergency stop behavior
* Python threading and command queue
* End-to-end robot movement test

---

## Phase 2 — Planned

The next version will focus on improving the perception and robotics stack.

Planned work:

* ROS2-based communication
* More reliable command handling
* Real-time object detection instead of VLM-based navigation
* YOLO + TensorRT optimization
* Better obstacle avoidance
* Improved motor control
* Encoder-based movement feedback
* More structured navigation logic

---

## What I Learned

This project gave me hands-on experience with:

* Raspberry Pi development
* Arduino and embedded motor control
* Camera integration
* Serial communication
* Python multithreading
* Producer/consumer queues
* Vision-Language Models
* Edge AI concepts
* ToF distance sensing
* Motor drivers
* Power management
* Hardware/software integration

The project is still a prototype, but the main purpose was to build and test the complete pipeline from **camera input → AI decision → embedded control → physical movement**.
