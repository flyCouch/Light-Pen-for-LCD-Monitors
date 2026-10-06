# USB LCD Light Pen (Structured Light Binary Search)

A high-performance, lag-free light pen system designed for modern **LCD monitors**. 

While traditional light pens invented in the 1950s rely entirely on CRT raster-scan electron beams, this project uses **temporal structured light (binary search)** rendered via GPU to bring light-pen functionality back to flat-panel displays. By flashing a rapid sequence of binary stripe patterns, an Arduino microcontroller decodes the coordinates locally in under half a second.

---

## How It Works: The 20-Frame Binary Search Handshake

Instead of scanning every single pixel or relying on slow raster sweeps, the system uses a logarithmic **binary search** across 20 frames (10 bits for X, 10 bits for Y):

1. **Spatial Splitting ($2^{10} = 1024$ steps):** 
   * Python projects a sequence of vertical and horizontal black-and-white stripe patterns.
   * **Frame 1 (MSB):** Splits the screen down the exact middle (left is black, right is white). If your sensor detects light, the highest bit is `1`; if dark, it's `0`.
   * **Frames 2–10:** Progressively finer vertical stripes halve the search space ($512$px, $256$px, down to $1$px), pinpointing the exact horizontal X coordinate.
   * **Frames 11–20:** Repeats the exact same binary halving process horizontally to resolve the Y coordinate.
2. **Synchronized Handshake Protocol:**
   * To prevent timing drift and ensure LCD pixels have physically transitioned before reading, Python uses a strict frame-by-frame trigger protocol. 
   * Python draws a pattern $\rightarrow$ waits briefly for pixel stabilization $\rightarrow$ sends an `'F'` command over USB $\rightarrow$ Arduino samples the digital light sensor pin precisely on command, bit-shifting the result into local memory.

---

## Hardware Requirements

* **Microcontroller:** Arduino Nano (or Uno/compatible).
* **Sensor:** Active-low/active-high digital light sensor module (e.g., photoresistor/phototransistor with an LM393 comparator) connected to digital pin **A2**.
* **Display:** Any standard LCD monitor.

---


