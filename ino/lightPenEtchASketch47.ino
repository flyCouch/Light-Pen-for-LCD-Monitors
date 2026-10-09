/*
   Project Name: USB Light Pen Binary Search Scanner (Dynamic Threshold)
   File: lightPenEtchASketch66.ino
   Date: 2026-10-09
   Time: 10:58:00
*/

void printHeader() {
  Serial.println(F("========================================"));
  Serial.print(F("PROJECT:  USB Light Pen Binary Search Scanner\n"));
  Serial.print(F("FILE:     ")); Serial.println(F(__FILE__));
  Serial.print(F("COMPILED: ")); Serial.print(F(__DATE__));
  Serial.print(F(" | "));      Serial.println(F(__TIME__));
  Serial.println(F("========================================\n"));
}

const int sensorPin = A2; 
const int buttonPin = A0; 

int xBits = 6;  
int yBits = 6;
int totalFrames = 12;
int analogThreshold = 700; // Default threshold

bool lastButtonState = LOW;

void setup() {
  Serial.begin(115200);
  delay(1000);
  printHeader();
  
  pinMode(buttonPin, INPUT);

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
  bool currentButtonState = digitalRead(buttonPin);

  if (currentButtonState == HIGH && lastButtonState == LOW) {
    Serial.println(F("START_SCAN"));

    long xCoord = 0;
    long yCoord = 0;

    for (int f = 0; f < totalFrames; f++) {
      unsigned long frameWait = millis();
      while (Serial.available() == 0) {
        if (millis() - frameWait > 500) break;
      }

      char cmd = Serial.read();
      if (cmd != 'F') continue;

      long analogSum = 0;
      int samples = 8;
      for (int s = 0; s < samples; s++) {
        analogSum += analogRead(sensorPin);
        delayMicroseconds(200);
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

    delay(50);
  }

  lastButtonState = currentButtonState;
}
