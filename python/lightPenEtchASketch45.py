# Project Name: Pygame USB Light Pen Binary Search Canvas (Debug Live)
# File: light_pen_binary_canvas.py
# Date: 2026-10-06
# Time: 08:00:00

import time
import pygame
import serial
import serial.tools.list_ports

WIDTH, HEIGHT = 800, 600
X_BITS = 10
Y_BITS = 10
FRAME_DELAY = 40 # Increased slightly to give LCD pixels plenty of time to switch


def select_serial_port():
  ports = list(serial.tools.list_ports.comports())
  if not ports:
    return None
  for index, port in enumerate(ports):
    print(f"  [{index}] {port.device} - {port.description}")
  choice = input("Enter port number: ")
  return ports[int(choice)].device


PORT = select_serial_port()
BAUD = 115200
ser = serial.Serial(PORT, BAUD, timeout=0.5) if PORT else None
time.sleep(2)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("USB Light Pen Binary Search Canvas")

drawing_srf = pygame.Surface((WIDTH, HEIGHT))
drawing_srf.fill((0, 0, 0))

running = True
clock = pygame.time.Clock()

print(f"Canvas ready ({WIDTH}x{HEIGHT}). Press SPACE to run binary scan!")

while running:
  screen.fill((0, 0, 0))
  screen.blit(drawing_srf, (0, 0))

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_SPACE:
        print("Executing synchronized binary scan...")
        if ser and ser.is_open:
          ser.reset_input_buffer()
          ser.write(b"B")

        # Pre-generate surfaces
        x_surfaces = []
        for bit in range(X_BITS):
          surf = pygame.Surface((WIDTH, HEIGHT))
          surf.fill((0, 0, 0))
          stripe_width = max(1, WIDTH // (2 ** (bit + 1)))
          for x_pos in range(0, WIDTH, stripe_width * 2):
            pygame.draw.rect(surf, (255, 255, 255), (x_pos, 0, stripe_width, HEIGHT))
          x_surfaces.append(surf)

        y_surfaces = []
        for bit in range(Y_BITS):
          surf = pygame.Surface((WIDTH, HEIGHT))
          surf.fill((0, 0, 0))
          stripe_height = max(1, HEIGHT // (2 ** (bit + 1)))
          for y_pos in range(0, HEIGHT, stripe_height * 2):
            pygame.draw.rect(surf, (255, 255, 255), (0, y_pos, WIDTH, stripe_height))
          y_surfaces.append(surf)

        all_surfs = x_surfaces + y_surfaces
        for i, surf in enumerate(all_surfs):
          screen.blit(drawing_srf, (0, 0))
          screen.blit(surf, (0, 0))
          pygame.display.flip()

          pygame.time.delay(FRAME_DELAY)

          if ser and ser.is_open:
            ser.write(b"F")

        # Clear scan visuals
        screen.fill((0, 0, 0))
        screen.blit(drawing_srf, (0, 0))
        pygame.display.flip()

        # Read resolved coordinate or debug prints from Arduino
        detected_x, detected_y = None, None
        if ser and ser.is_open:
          start_wait = time.time()
          while time.time() - start_wait < 1.0:
            if ser.in_waiting > 0:
              line = ser.readline().decode("utf-8", errors="ignore").strip()
              print(f"Arduino says: {line}")  # Print everything Arduino sends
              if "COORD:" in line:
                parts = line.replace("COORD:", "").split(",")
                if len(parts) == 2:
                  detected_x = int(parts[0])
                  detected_y = int(parts[1])
                  break

        if detected_x is not None and detected_y is not None:
          detected_x = max(0, min(WIDTH - 1, detected_x))
          detected_y = max(0, min(HEIGHT - 1, detected_y))
          pygame.draw.circle(drawing_srf, (0, 255, 0), (detected_x, detected_y), 20)
          print(f"Successfully Mapped point: ({detected_x}, {detected_y})")
        else:
          print("Scan complete: No valid coordinate received.")

  pygame.display.flip()
  clock.tick(60)

if ser and ser.is_open:
  ser.close()
pygame.quit()
