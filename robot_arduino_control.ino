#include "Adafruit_VL53L0X.h"

// --- PINS ---
#define ENA 5  // Rear Drive
#define IN1 8
#define IN2 9
#define ENB 6  // Front Steer
#define IN3 11
#define IN4 10

// --- LASER ---
Adafruit_VL53L0X lox = Adafruit_VL53L0X();
const int SAFE_DISTANCE_MM = 300; // Increased to 30cm for safety!
bool path_blocked = false;

void setup() {
  Serial.begin(9600);
  Wire.begin();
  if (!lox.begin()) {
    Serial.println("ERROR: Laser not found!");
  } else {
    Serial.println("Laser ready!");
  }

  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(ENB, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
}

void stopCar() {
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}

void loop() {
  // 1. SAFETY CHECK FIRST
  VL53L0X_RangingMeasurementData_t measure;
  lox.rangingTest(&measure, false);
  int distance = measure.RangeMilliMeter;

  // Check if a real object is closer than 30cm
  if (measure.RangeStatus != 4 && distance > 0 && distance < SAFE_DISTANCE_MM) {
    path_blocked = true;
    stopCar(); // INSTANT FREEZE
  } else {
    path_blocked = false;
  }

  // 2. COMMAND EXECUTION
  if (Serial.available() > 0) {
    char command = Serial.read();
    
    // If path is blocked, ONLY allow turning or stopping. Ignore Forward/Creep.
    if (path_blocked) {
      if (command == 'L') {
        // MOVING LEFT
        digitalWrite(IN3, HIGH);
        digitalWrite(IN4, LOW);
        analogWrite(ENB, 255);
        digitalWrite(IN1, HIGH);
        digitalWrite(IN2, LOW);
        analogWrite(ENA, 128); 
        delay(800);
        stopCar();
      } 
      else if (command == 'R') {
        // MOVING RIGHT
        digitalWrite(IN3, LOW);
        digitalWrite(IN4, HIGH);
        analogWrite(ENB, 255);
        digitalWrite(IN1, HIGH);
        digitalWrite(IN2, LOW);
        analogWrite(ENA, 128); 
        delay(800);
        stopCar();
      } 
      else if (command == 'S') {
        stopCar();
      }
      // If command is 'C' or 'F', we ignore it! The car stays frozen.
    } 
    else {
      // Path is clear! Normal operation.
      if (command == 'C') {
        digitalWrite(IN1, HIGH);
        digitalWrite(IN2, LOW);
        analogWrite(ENA, 90); // Creep speed
        analogWrite(ENB, 0);  // Center steering
      } 
      else if (command == 'F') {
        digitalWrite(IN1, HIGH);
        digitalWrite(IN2, LOW);
        analogWrite(ENA, 255); // Full power
        delay(1500);
        stopCar();
      } 
      else if (command == 'L') {
        digitalWrite(IN3, HIGH);
        digitalWrite(IN4, LOW);
        analogWrite(ENB, 255);
        digitalWrite(IN1, HIGH);
        digitalWrite(IN2, LOW);
        analogWrite(ENA, 128); 
        delay(800);
        stopCar();
      } 
      else if (command == 'R') {
        digitalWrite(IN3, LOW);
        digitalWrite(IN4, HIGH);
        analogWrite(ENB, 255);
        digitalWrite(IN1, HIGH);
        digitalWrite(IN2, LOW);
        analogWrite(ENA, 128); 
        delay(800);
        stopCar();
      } 
      else if (command == 'S') {
        stopCar();
      }
    }
  }
}
