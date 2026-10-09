# Project Name: Pygame USB Light Pen Binary Search Canvas (Force Clear Fix)
# File: lightPenEtchASketch72.py
# Date: 2026-10-09
# Time: 11:32:00

import time
import pygame
import serial
import serial.tools.list_ports

# --- CONFIGURABLE PARAMETERS ---
WIN_WIDTH, WIN_HEIGHT = 1280, 768
CANVAS_WIDTH = 1024
CANVAS_HEIGHT = 768

VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 1024, 1024
BASE_X_BITS = 10
BASE_Y_BITS = 10
FRAME_DELAY = 60

X_OFFSET = 0
Y_OFFSET = 0

# 1. Initialize Pygame immediately so window pops up
print("=== USB LIGHT PEN SETUP ===")
pygame.init()
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("USB Light Pen Binary Search Canvas")

drawing_srf = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
drawing_srf.fill((0, 0, 0))
font = pygame.font.SysFont(None, 24)

# Render initial blank screen instantly
screen.fill((0, 0, 0))
screen.blit(drawing_srf, (0, 0))
pygame.display.flip()

# 2. Terminal setup prompts
try:
  drop_lsbs = int(
      input("Enter number of LSBs to drop (de-accuratize) [Default 4]: ") or "4"
  )
except ValueError:
  drop_lsbs = 4

try:
  threshold = int(
      input("Enter analog threshold level [Default 700]: ") or "700"
  )
except ValueError:
  threshold = 700

X_BITS = max(1, BASE_X_BITS - drop_lsbs)
Y_BITS = max(1, BASE_Y_BITS - drop_lsbs)
coarse_factor = 2**drop_lsbs

print(
    f"Active Scan Resolution: {X_BITS} X-bits, {Y_BITS} Y-bits | Threshold:"
    f" {threshold} | Coarse Block Size: {coarse_factor}px"
)

COLORS = {
    pygame.K_1: (0, 255, 0),
    pygame.K_2: (255, 0, 0),
    pygame.K_3: (0, 0, 255),
    pygame.K_4: (255, 255, 0),
    pygame.K_5: (0, 255, 255),
    pygame.K_6: (255, 0, 255),
    pygame.K_7: (255, 255, 255),
    pygame.K_8: (255, 128, 0),
    pygame.K_9: (128, 0, 255),
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

print(
    f"Project: Pygame USB Light Pen | File: lightPenEtchASketch72.py | Date:"
    f" 2026-10-09 | Baud: {BAUD}"
)


def draw_sidebar():
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
      f"LSB Dropped: {drop_lsbs}",
      f"Threshold: {threshold}",
      f"Block Res: {coarse_factor}px",
      f"X-Offset: {X_OFFSET}",
      f"Y-Offset: {Y_OFFSET}",
      "[1-9] : Change Color",
      "[0]   : Erase (Black)",
      "[C]   : Clear Screen",
      "[Q]   : Quit App",
  ]
  for i, text in enumerate(lines):
    txt_surf = font.render(text, True, (255, 255, 255))
    screen.blit(txt_surf, (CANVAS_WIDTH + 15, 20 + (i * 30)))

  color_label_surf = font.render("CURRENT COLOR:", True, (255, 255, 255))
  screen.blit(color_label_surf, (CANVAS_WIDTH + 15, 380))

  swatch_rect = pygame.Rect(CANVAS_WIDTH + 15, 410, 80, 40)
  pygame.draw.rect(screen, current_color, swatch_rect)
  pygame.draw.rect(screen, (255, 255, 255), swatch_rect, 2)


# Connect Serial
ser = serial.Serial(PORT, BAUD, timeout=0.1) if PORT else None
time.sleep(2)

if ser and ser.is_open:
  ser.reset_input_buffer()
  ser.reset_output_buffer()
  time.sleep(1)
  config_msg = f"CONFIG:{X_BITS},{Y_BITS},{threshold}\n"
  ser.write(config_msg.encode("utf-8"))
  time.sleep(0.5)

print("Pre-generating de-accuratized binary scan patterns...")
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

clock = pygame.time.Clock()
running = True

while running:
  # 1. Event Handling
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_q:
        running = False
      elif event.key == pygame.K_c:
        # FORCE immediate wipe of both memory surface and active display buffer
        drawing_srf.fill((0, 0, 0))
        screen.fill((0, 0, 0))
        screen.blit(drawing_srf, (0, 0))
        draw_sidebar()
        pygame.display.flip()
        print("Screen cleared.")
      elif event.key == pygame.K_0:
        current_color = (0, 0, 0)
        print("Eraser selected.")
      elif event.key in COLORS:
        current_color = COLORS[event.key]
        print(f"Color changed to {current_color}")

  # 2. Serial communication check
  if ser and ser.is_open and ser.in_waiting > 0:
    line = ser.readline().decode("utf-8", errors="ignore").strip()

    if "START_SCAN" in line:
      for surf in all_surfs:
        screen.fill((0, 0, 0))
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
          coarse_x = int(parts[0])
          coarse_y = int(parts[1])

          virt_x = (coarse_x * coarse_factor) + (coarse_factor // 2)
          virt_y = (coarse_y * coarse_factor) + (coarse_factor // 2)

          detected_x = int(virt_x * (CANVAS_WIDTH / VIRTUAL_WIDTH)) + X_OFFSET
          detected_y = int(virt_y * (CANVAS_HEIGHT / VIRTUAL_HEIGHT)) + Y_OFFSET

          detected_x = max(0, min(CANVAS_WIDTH - 1, detected_x))
          detected_y = max(0, min(CANVAS_HEIGHT - 1, detected_y))

          pygame.draw.circle(
              drawing_srf, current_color, (detected_x, detected_y), brush_size
          )
          print(
              f"Drawn point: ({detected_x}, {detected_y}) [Coarse:"
              f" {coarse_x},{coarse_y}]"
          )
        except ValueError:
          pass
    else:
      if line:
        print(f"Arduino: {line}")

  # 3. Continuous render loop
  screen.fill((0, 0, 0))
  screen.blit(drawing_srf, (0, 0))
  draw_sidebar()
  pygame.display.flip()
  clock.tick(60)

if ser and ser.is_open:
  ser.close()
pygame.quit()
