/*
 * Project Name: USB Light Pen Binary Search Scanner (Button Hold)
 * File: lightPenEtchASketch24.ino
 * Date: 2026-10-06
 * Time: 11:15:00
 */

// Project Header Prints
void printHeader() {
  Serial.println(F("========================================"));
  Serial.print(F("PROJECT:  USB Light Pen Binary Search Scanner\n"));
  Serial.print(F("FILE:     ")); Serial.println(F(__FILE__));
  Serial.print(F("COMPILED: ")); Serial.print(F(__DATE__));
  Serial.print(F(" | "));      Serial.println(F(__TIME__));
  Serial.println(F("========================================\n"));
}

const int sensorPin = A2; 
const int buttonPin = A0; // Tactile switch connected to 3.3V and A0
const int X_BITS = 10;
const int Y_BITS = 10;
const int TOTAL_FRAMES = X_BITS + Y_BITS;

void setup() {
  Serial.begin(115200);
  printHeader();
  pinMode(sensorPin, INPUT);
  pinMode(buttonPin, INPUT);
}

void loop() {
  if (digitalRead(buttonPin) == HIGH) {
    Serial.println(F("START_SCAN"));

    long xCoord = 0;
    long yCoord = 0;
    
    for (int f = 0; f < TOTAL_FRAMES; f++) {
      Serial.print(F("REQ_FRAME_"));
      Serial.println(f);

      unsigned long waitStart = millis();
      while (Serial.available() == 0) {
        if (millis() - waitStart > 1000) return;
      }
      
      char frameCmd = Serial.read();
      if (frameCmd != 'F') continue;

      int sensorState = digitalRead(sensorPin);
      int bitVal = (sensorState == HIGH) ? 1 : 0;

      if (f < X_BITS) {
        if (bitVal == 1) {
          xCoord |= (1L << (X_BITS - 1 - f));
        }
      } else {
        int yIndex = f - X_BITS;
        if (bitVal == 1) {
          yCoord |= (1L << (Y_BITS - 1 - yIndex));
        }
      }
    }

    if (xCoord < 0) xCoord = 0;
    if (xCoord > 1023) xCoord = 1023;
    if (yCoord < 0) yCoord = 0;
    if (yCoord > 1023) yCoord = 1023;

    // UPDATED: Scale strictly to the new 1024x768 drawing canvas size!
    int finalX = (int)((xCoord * 1024L) / 1023L);
    int finalY = (int)((yCoord * 768L) / 1023L);

    Serial.print(F("COORD:"));
    Serial.print(finalX);
    Serial.print(F(","));
    Serial.println(finalY);

    delay(10);
  }
}
