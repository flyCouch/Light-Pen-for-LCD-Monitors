# Project Name: Pygame Shrinking Box Etch-a-Sketch with LSB Controls
# File: lightPenEtchASketch220.py
# Date: 2026-10-10
# Time: 23:45:00

import time
import pygame
import serial
import serial.tools.list_ports

# --- CONFIGURABLE PARAMETERS ---
WIN_WIDTH, WIN_HEIGHT = 1280, 768
CANVAS_WIDTH = 1024
CANVAS_HEIGHT = 768

VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 1024, 1024
SETTLE_DELAY = 60

print("=== USB LIGHT PEN SHRINKING BOX + LSB CONTROLS ===")
pygame.init()
screen = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("USB Light Pen - Shrinking Box + LSBs")

drawing_srf = pygame.Surface((CANVAS_WIDTH, CANVAS_HEIGHT))
drawing_srf.fill((0, 0, 0))
font = pygame.font.SysFont(None, 24)

screen.fill((0, 0, 0))
screen.blit(drawing_srf, (0, 0))
pygame.display.flip()

# Terminal setup prompts
try:
  drop_lsbs = int(
      input("Enter number of LSBs to drop (de-accuratize) [Default 2]: ") or "2"
  )
except ValueError:
  drop_lsbs = 2

try:
  threshold = int(
      input("Enter active-low analog threshold level [Default 400]: ") or "400"
  )
except ValueError:
  threshold = 400

# Calculate generations and coarse factor based on LSB drop
generations = max(2, 5 - (drop_lsbs // 2))
coarse_factor = 2**drop_lsbs

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
brush_size = max(10, coarse_factor)


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
      "SHRINKING BOX + LSB",
      "-------------------",
      f"LSB Dropped: {drop_lsbs}",
      f"Threshold: {threshold}",
      f"Generations: {generations}",
      f"Block Size: {coarse_factor}px",
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


ser = serial.Serial(PORT, BAUD, timeout=0.1) if PORT else None
time.sleep(2)

if ser and ser.is_open:
  ser.reset_input_buffer()
  ser.reset_output_buffer()
  time.sleep(1)
  config_msg = f"CONFIG:{drop_lsbs},{threshold}\n"
  ser.write(config_msg.encode("utf-8"))
  time.sleep(0.5)


def flash_and_read(x, y, w, h):
  surf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
  surf.fill((0, 0, 0))

  w = max(1, w)
  h = max(1, h)
  pygame.draw.rect(surf, (255, 255, 255), (x, y, w, h))

  scaled_surf = pygame.transform.smoothscale(
      surf, (CANVAS_WIDTH, CANVAS_HEIGHT)
  )

  screen.fill((0, 0, 0))
  screen.blit(drawing_srf, (0, 0))
  screen.blit(scaled_surf, (0, 0))
  draw_sidebar()
  pygame.display.flip()

  pygame.time.delay(SETTLE_DELAY)

  if ser and ser.is_open:
    ser.reset_input_buffer()
    ser.write(b"Q")
    ser.flush()

  deadline = time.time() + 0.3
  while time.time() < deadline:
    if ser.in_waiting > 0:
      line = ser.readline().decode("utf-8", errors="ignore").strip()
      if line.startswith("VAL:"):
        try:
          return int(line.split("VAL:")[1])
        except ValueError:
          pass
  return 1023


clock = pygame.time.Clock()
running = True

while running:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      running = False
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_q:
        running = False
      elif event.key == pygame.K_c:
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

  if ser and ser.is_open and ser.in_waiting > 0:
    line = ser.readline().decode("utf-8", errors="ignore").strip()

    if "START_SCAN" in line:
      ser.reset_input_buffer()

      # Start with full virtual box
      bx, by, bw, bh = 0, 0, VIRTUAL_WIDTH, VIRTUAL_HEIGHT

      # Run dynamic shrinking generations based on LSB setting
      for gen in range(generations):
        hw, hh = bw // 2, bh // 2
        q_tl = (bx, by, hw, hh)
        q_tr = (bx + hw, by, hw, hh)
        q_bl = (bx, by + hh, hw, hh)
        q_br = (bx + hw, by + hh, hw, hh)

        v_tl = flash_and_read(*q_tl)
        v_tr = flash_and_read(*q_tr)
        v_bl = flash_and_read(*q_bl)
        v_br = flash_and_read(*q_br)

        quads = [(v_tl, q_tl), (v_tr, q_tr), (v_bl, q_bl), (v_br, q_br)]
        _, (bx, by, bw, bh) = min(quads, key=lambda item: item[0])

      # Map to virtual center and apply LSB quantization (coarse grid snap)
      virt_x = bx + (bw // 2)
      virt_y = by + (bh // 2)

      if coarse_factor > 1:
        coarse_x = virt_x // coarse_factor
        coarse_y = virt_y // coarse_factor
        virt_x = (coarse_x * coarse_factor) + (coarse_factor // 2)
        virt_y = (coarse_y * coarse_factor) + (coarse_factor // 2)

      detected_x = int(virt_x * (CANVAS_WIDTH / VIRTUAL_WIDTH))
      detected_y = int(virt_y * (CANVAS_HEIGHT / VIRTUAL_HEIGHT))

      detected_x = max(0, min(CANVAS_WIDTH - 1, detected_x))
      detected_y = max(0, min(CANVAS_HEIGHT - 1, detected_y))

      pygame.draw.circle(
          drawing_srf, current_color, (detected_x, detected_y), brush_size
      )

      screen.fill((0, 0, 0))
      screen.blit(drawing_srf, (0, 0))
      draw_sidebar()
      pygame.display.flip()

    else:
      if line:
        print(f"Arduino: {line}")

  screen.fill((0, 0, 0))
  screen.blit(drawing_srf, (0, 0))
  draw_sidebar()
  pygame.display.flip()
  clock.tick(60)

if ser and ser.is_open:
  ser.close()
pygame.quit()
