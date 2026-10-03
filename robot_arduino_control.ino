#include "Adafruit_VL53L0X.h"


// Motor pins
#define ENA 5
#define IN1 8
#define IN2 9

#define ENB 6
#define IN3 11
#define IN4 10


// Distance sensor
Adafruit_VL53L0X lox = Adafruit_VL53L0X();

const int SAFE_DISTANCE_MM = 300;

bool path_blocked = false;


void setup() {
  Serial.begin(9600);
  Wire.begin();

  // Start the distance sensor
  if (!lox.begin()) {
    Serial.println("Laser sensor not found");
  } else {
    Serial.println("Laser sensor ready");
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

  // Check the distance before doing anything else
  VL53L0X_RangingMeasurementData_t measure;

  lox.rangingTest(&measure, false);

  int distance = measure.RangeMilliMeter;

  if (measure.RangeStatus != 4 &&
      distance > 0 &&
      distance < SAFE_DISTANCE_MM) {

    path_blocked = true;
    stopCar();

  } else {
    path_blocked = false;
  }


  // Check for commands from the Raspberry Pi
  if (Serial.available() > 0) {

    char command = Serial.read();


    if (path_blocked) {

      // if something infrnt stop it.
      // turning allowed.

      if (command == 'L') {

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

      // Ignore F and C while the path is blocked.
    }


    else {

      // Path is clear, so process the normal commands.

      if (command == 'C') {

        // Slow movement while waiting for the next decision
        digitalWrite(IN1, HIGH);
        digitalWrite(IN2, LOW);

        analogWrite(ENA, 90);
        analogWrite(ENB, 0);

      }

      else if (command == 'F') {

        // Move forward at full speed
        digitalWrite(IN1, HIGH);
        digitalWrite(IN2, LOW);

        analogWrite(ENA, 255);

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
