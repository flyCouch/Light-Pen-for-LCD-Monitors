/*
   Project Name: Shrinking Box Light Pen with Configurable LSBs
   File: lightPenEtchASketch220.ino
   Date: 2026-10-10
   Time: 23:45:00
*/

const int sensorPin = A2; 
const int buttonPin = A0; 

int dropLsbs = 2;
int generations = 4; // Dynamic steps based on resolution
int totalSteps = 16;
int analogThreshold = 400;

void setup() {
  Serial.begin(115200);
  delay(1000);
  
  // --- START PROJECT HEADER PRINT ---
  Serial.println(F("\n========================================"));
  Serial.print(F("FILE:     ")); Serial.println(F(__FILE__));
  Serial.print(F("COMPILED: ")); Serial.print(F(__DATE__));
  Serial.print(F(" | "));      Serial.println(F(__TIME__));
  Serial.println(F("========================================\n"));
  // --- END PROJECT HEADER PRINT ---

  pinMode(buttonPin, INPUT);

  // Listen for Python's config string: CONFIG:DROP,THRESHOLD
  unsigned long startWait = millis();
  while (millis() - startWait < 2000) {
    if (Serial.available() > 0) {
      String msg = Serial.readStringUntil('\n');
      msg.trim();
      if (msg.startsWith("CONFIG:")) {
        int commaIdx = msg.indexOf(',');
        if (commaIdx != -1) {
          dropLsbs = msg.substring(7, commaIdx).toInt();
          analogThreshold = msg.substring(commaIdx + 1).toInt();
          
          // Calculate generations based on LSB drop (e.g., drop 0 = 5 gens, drop 4 = 3 gens)
          generations = max(2, 5 - (dropLsbs / 2));
          totalSteps = generations * 4;

          Serial.print(F("ACK_DROP=")); Serial.print(dropLsbs);
          Serial.print(F("_GENS=")); Serial.println(generations);
          break;
        }
      }
    }
  }
}

void loop() {
  while (digitalRead(buttonPin) == HIGH) {
    Serial.println(F("START_SCAN"));

    for (int step = 0; step < totalSteps; step++) {
      unsigned long frameWait = millis();
      while (Serial.available() == 0) {
        if (millis() - frameWait > 200) break;
      }

      char cmd = Serial.read();
      if (cmd != 'Q') continue;

      long analogSum = 0;
      int samples = 12;
      for (int s = 0; s < samples; s++) {
        analogSum += analogRead(sensorPin);
        delayMicroseconds(30);
      }
      int avgAnalog = analogSum / samples;

      Serial.print(F("VAL:"));
      Serial.println(avgAnalog);
    }
    
    delay(10);
  }
}
