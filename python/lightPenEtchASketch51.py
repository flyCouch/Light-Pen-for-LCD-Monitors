# Project Name: Pygame USB Light Pen Binary Search Canvas (Sidebar Controls)
# File: lightPenEtchASketch51.py
# Date: 2026-10-06
# Time: 11:00:00

import time
import pygame
import serial
import serial.tools.list_ports

# --- CONFIGURABLE PARAMETERS ---
# We make the total window 1280 wide: 1024 for drawing, 256 for the sidebar controls
WIN_WIDTH, WIN_HEIGHT = 1280, 768
CANVAS_WIDTH = 1024
CANVAS_HEIGHT = 768

VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 1024, 1024
X_BITS = 10
Y_BITS = 10
FRAME_DELAY = 40  # LCD pixel stabilization delay

# Color Palette Mapping (Number keys 1-9)
COLORS = {
    pygame.K_1: (0, 255, 0),  # Green (Default)
    pygame.K_2: (255, 0, 0),  # Red
    pygame.K_3: (0, 0, 255),  # Blue
    pygame.K_4: (255, 255, 0),  # Yellow
    pygame.K_5: (0, 255, 255),  # Cyan
    pygame.K_6: (255, 0, 255),  # Magenta
    pygame.K_7: (255, 255, 255),  # White
    pygame.K_8: (255, 128, 0),  # Orange
    pygame.K_9: (128, 0, 255),  # Purple
}
current_color = (0, 255, 0)
brush_size = 20


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
ser = serial.Serial(PORT, BAUD, timeout=0.1) if PORT else None
time.sleep(2)

pygame.init()

# Main unified window
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("USB Light Pen Binary Search Canvas")

drawing_srf = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
drawing_srf.fill((0, 0, 0))

running = True
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 24)

# Pre-generate 10-bit patterns scaled to 1024x768 canvas
print("Pre-generating binary scan patterns...")
x_surfaces = []
for bit in range(X_BITS):
  surf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
  surf.fill((0, 0, 0))
  stripe_width = VIRTUAL_WIDTH // (2 ** (bit + 1))
  for x_pos in range(0, VIRTUAL_WIDTH, stripe_width * 2):
    pygame.draw.rect(
        surf, (255, 255, 255), (x_pos, 0, stripe_width, VIRTUAL_HEIGHT)
    )
  x_surfaces.append(
      pygame.transform.smoothscale(surf, (CANVAS_WIDTH, CANVAS_HEIGHT))
  )

y_surfaces = []
for bit in range(Y_BITS):
  surf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
  surf.fill((0, 0, 0))
  stripe_height = VIRTUAL_HEIGHT // (2 ** (bit + 1))
  for y_pos in range(0, VIRTUAL_HEIGHT, stripe_height * 2):
    pygame.draw.rect(
        surf, (255, 255, 255), (0, y_pos, VIRTUAL_WIDTH, stripe_height)
    )
  y_surfaces.append(
      pygame.transform.smoothscale(surf, (CANVAS_WIDTH, CANVAS_HEIGHT))
  )

all_surfs = x_surfaces + y_surfaces

print(
    f"Canvas ready ({CANVAS_WIDTH}x{CANVAS_HEIGHT}). Hold down your pen button"
    " to draw live!"
)


def draw_sidebar():
  # Sidebar background
  sidebar_rect = pygame.Rect(CANVAS_WIDTH, 0, WIN_WIDTH - CANVAS_WIDTH, WIN_HEIGHT)
  pygame.draw.rect(screen, (40, 40, 40), sidebar_rect)
  pygame.draw.line(
      screen,
      (100, 100, 100),
      (CANVAS_WIDTH, 0),
      (CANVAS_WIDTH, WIN_HEIGHT),
      2,
  )

  lines = [
      "LIGHT PEN CONTROLS",
      "------------------",
      "[1-9] : Change Color",
      "[0]   : Erase (Black)",
      "[C]   : Clear Screen",
      "[Q]   : Quit App",
      "",
      "CURRENT COLOR:",
  ]

  for i, text in enumerate(lines):
    txt_surf = font.render(text, True, (255, 255, 255))
    screen.blit(txt_surf, (CANVAS_WIDTH + 15, 20 + (i * 30)))

  # Color swatch preview box
  swatch_rect = pygame.Rect(CANVAS_WIDTH + 15, 260, 80, 40)
  pygame.draw.rect(screen, current_color, swatch_rect)
  pygame.draw.rect(screen, (255, 255, 255), swatch_rect, 2)


while running:
  screen.fill((0, 0, 0))
  # Blit drawing canvas on the left
  screen.blit(drawing_srf, (0, 0))
  # Draw sidebar controls on the right
  draw_sidebar()

  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False

    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_q:
        running = False
      elif event.key == pygame.K_c:
        drawing_srf.fill((0, 0, 0))
        print("Screen cleared.")
      elif event.key == pygame.K_0:
        current_color = (0, 0, 0)  # Erase mode
        print("Eraser selected.")
      elif event.key in COLORS:
        current_color = COLORS[event.key]
        print(f"Color changed to {current_color}")

  # Listen to Arduino for continuous button-hold drawing scans
  if ser and ser.is_open and ser.in_waiting > 0:
    line = ser.readline().decode("utf-8", errors="ignore").strip()

    if "START_SCAN" in line:
      for surf in all_surfs:
        screen.blit(drawing_srf, (0, 0))
        screen.blit(surf, (0, 0))
        draw_sidebar()
        pygame.display.flip()

        pygame.time.delay(FRAME_DELAY)

        if ser and ser.is_open:
          ser.write(b"F")

      screen.fill((0, 0, 0))
      screen.blit(drawing_srf, (0, 0))
      draw_sidebar()
      pygame.display.flip()

    elif "COORD:" in line:
      parts = line.replace("COORD:", "").split(",")
      if len(parts) == 2:
        try:
          detected_x = int(parts[0])
          detected_y = int(parts[1])
          # Clamp strictly to the active drawing area
          detected_x = max(0, min(CANVAS_WIDTH - 1, detected_x))
          detected_y = max(0, min(CANVAS_HEIGHT - 1, detected_y))
          pygame.draw.circle(
              drawing_srf, current_color, (detected_x, detected_y), brush_size
          )
          print(
              f"Drawn point: ({detected_x}, {detected_y}) with color"
              f" {current_color}"
          )
        except ValueError:
          pass

  pygame.display.flip()
  clock.tick(60)

if ser and ser.is_open:
  ser.close()
pygame.quit()
