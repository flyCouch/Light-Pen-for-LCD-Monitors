/*
   Project Name: USB Light Pen Binary Search Scanner (Continuous Chaining)
   File: lightPenEtchASketch75.ino
   Date: 2026-10-09
   Time: 11:55:00
*/

const int sensorPin = A2; 
const int buttonPin = A0; 

int xBits = 6;  
int yBits = 6;
int totalFrames = 12;
int analogThreshold = 700;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // --- START INTERNAL ID SNIPPET ---
  Serial.println(F("\n========================================"));
  Serial.print(F("FILE:     ")); Serial.println(F(__FILE__));
  Serial.print(F("COMPILED: ")); Serial.print(F(__DATE__));
  Serial.print(F(" | "));      Serial.println(F(__TIME__));
  Serial.println(F("========================================\n"));
  // --- END INTERNAL ID SNIPPET ---

  
  pinMode(buttonPin, INPUT); // Hardware pull-down present, reading active-HIGH from 3.3V

  // Listen for Python's config string: CONFIG:X,Y,THRESHOLD
  unsigned long startWait = millis();
  while (millis() - startWait < 2000) {
    if (Serial.available() > 0) {
      String msg = Serial.readStringUntil('\n');
      msg.trim();
      if (msg.startsWith("CONFIG:")) {
        int firstComma = msg.indexOf(',');
        int secondComma = msg.indexOf(',', firstComma + 1);
        if (firstComma != -1) {
          xBits = msg.substring(7, firstComma).toInt();
          if (secondComma != -1) {
            yBits = msg.substring(firstComma + 1, secondComma).toInt();
            analogThreshold = msg.substring(secondComma + 1).toInt();
          } else {
            yBits = msg.substring(firstComma + 1).toInt();
          }
          totalFrames = xBits + yBits;
          Serial.print(F("ACK_X=")); Serial.print(xBits);
          Serial.print(F("_Y=")); Serial.print(yBits);
          Serial.print(F("_THR=")); Serial.println(analogThreshold);
          break;
        }
      }
    }
  }
}

void loop() {
  // Check if button is pressed (HIGH via 3.3V pull-down)
  if (digitalRead(buttonPin) == HIGH) {
    Serial.println(F("START_SCAN"));

    long xCoord = 0;
    long yCoord = 0;

    for (int f = 0; f < totalFrames; f++) {
      unsigned long frameWait = millis();
      while (Serial.available() == 0) {
        if (millis() - frameWait > 100) break; // Tight 100ms timeout
      }

      char cmd = Serial.read();
      if (cmd != 'F') continue;

      long analogSum = 0;
      int samples = 8;
      for (int s = 0; s < samples; s++) {
        analogSum += analogRead(sensorPin);
        delayMicroseconds(50);
      }
      int avgAnalog = analogSum / samples;

      int bitVal = (avgAnalog > analogThreshold) ? 1 : 0;

      if (f < xBits) {
        if (bitVal == 1) {
          xCoord |= (1L << (xBits - 1 - f));
        }
      } else {
        int yIndex = f - xBits;
        if (bitVal == 1) {
          yCoord |= (1L << (yBits - 1 - yIndex));
        }
      }
    }

    Serial.print(F("COORD:"));
    Serial.print(xCoord);
    Serial.print(F(","));
    Serial.println(yCoord);

    // Small breather so serial buffers can clear between chained scans
    delay(10);
  }
}
