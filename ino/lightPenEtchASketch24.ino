/*
 * Project Name: USB Light Pen Binary Search Scanner (Robust)
 * File: light_pen_binary_sensor.ino
 * Date: 2026-10-06
 * Time: 08:15:00
 */

const int sensorPin = A2; 
const int X_BITS = 10;
const int Y_BITS = 10;
const int TOTAL_FRAMES = X_BITS + Y_BITS;

void setup() {
  Serial.begin(115200);
  
  // Required Project Header Prints
  Serial.println(F("========================================"));
  Serial.print(F("PROJECT:  USB Light Pen Binary Search Scanner\n"));
  Serial.print(F("FILE:     ")); Serial.println(F(__FILE__));
  Serial.print(F("COMPILED: ")); Serial.print(F(__DATE__));
  Serial.print(F(" | "));      Serial.println(F(__TIME__));
  Serial.println(F("========================================\n"));

  pinMode(sensorPin, INPUT);
}

void loop() {
  if (Serial.available() > 0) {
    char cmd = Serial.read();
    if (cmd == 'B') {
      long xCoord = 0;
      long yCoord = 0;
      
      for (int f = 0; f < TOTAL_FRAMES; f++) {
        unsigned long waitStart = millis();
        while (Serial.available() == 0) {
          if (millis() - waitStart > 1000) return;
        }
        
        char frameCmd = Serial.read();
        if (frameCmd != 'F') continue;

        int sensorState = digitalRead(sensorPin);
        
        // If your sensor triggers HIGH on light, keep as (sensorState == HIGH) ? 1 : 0
        // If it triggers LOW on light, change to (sensorState == LOW) ? 1 : 0
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

      // Safety bounds check on raw 10-bit values
      if (xCoord < 0) xCoord = 0;
      if (xCoord > 1023) xCoord = 1023;
      if (yCoord < 0) yCoord = 0;
      if (yCoord > 1023) yCoord = 1023;

      // Scale strictly to 800x600 screen pixels
      int finalX = (int)((xCoord * 800L) / 1023L);
      int finalY = (int)((yCoord * 600L) / 1023L);

      Serial.print(F("COORD:"));
      Serial.print(finalX);
      Serial.print(F(","));
      Serial.println(finalY);
    }
  }
}
