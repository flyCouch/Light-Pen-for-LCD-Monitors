# USB LCD Light Pen (Structured Light Binary Search)

A high-performance, lag-free light pen system designed for modern **LCD monitors**. 

While traditional light pens invented in the 1950s rely entirely on CRT raster-scan electron beams, this project uses **temporal structured light (binary search)** rendered via GPU to bring light-pen functionality back to flat-panel displays. By flashing a rapid sequence of binary stripe patterns, an Arduino microcontroller decodes the coordinates locally in under half a second.

---

## Features
* **LCD-Compatible:** Bypasses traditional CRT raster requirements using GPU-accelerated temporal structured light.
* **Ergonomic Button-Hold Drawing:** Integrated tactile switch on pin `A0` allows you to hold down the button to draw continuously.
* **Live Color Palette & Erasing:** Switch colors on the fly using number keys (`1`–`9`), erase with `0`, clear the screen with `C`, or quit with `Q`.
* **High Resolution Canvas:** Operates on a 1024 x 768 active drawing area with an intuitive sidebar control panel.

---

## How It Works: The 20-Frame Binary Search Handshake

Instead of scanning every single pixel or relying on slow raster sweeps, the system uses a logarithmic **binary search** across 20 frames (10 bits for X, 10 bits for Y):

1. **Spatial Splitting (2^{10} = 1024 steps):** 
   * Python projects a sequence of vertical and horizontal black-and-white stripe patterns.
   * **Frame 1 (MSB):** Splits the screen down the exact middle (left is black, right is white). If your sensor detects light, the highest bit is `1`; if dark, it's `0`.
   * **Frames 2–10:** Progressively finer vertical stripes halve the search space down to $1$px, pinpointing the exact horizontal X coordinate.
   * **Frames 11–20:** Repeats the exact same binary halving process horizontally to resolve the Y coordinate.
2. **Synchronized Handshake Protocol:**
   * To prevent timing drift and ensure LCD pixels have physically transitioned before reading, Python uses a strict frame-by-frame trigger protocol. 
   * Python draws a pattern,waits for pixel stabilization, sends an `'F'` command over USB,Arduino samples the digital light sensor pin precisely on command, bit-shifting the result into local memory.

---

## Hardware Requirements

* **Microcontroller:** Arduino Nano (or Uno/compatible).
* **Sensors & Controls:** 
  * Digital light sensor module (e.g., photoresistor/phototransistor with an LM393 comparator) connected to pin **A2**.
  * Tactile push button connected between **3.3V** and pin **A0** (with a pull-down resistor to ground).
* **Display:** Any standard LCD monitor connected to a modern GPU.

---
use lightPenEtchASketch31Switch.ino with lightPenEtchASketch51.py

