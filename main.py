from machine import Pin
import utime
import os
from epd2in13v4 import EPD_2in13_V4_Landscape

SCREEN_W = 250  # actual framebuffer pixel width in landscape mode
SCREEN_H = 122  # actual framebuffer pixel height in landscape mode

PAGES_DIR = "/pages"
STATE_FILE = "/last_page.txt"

button_next = Pin(14, Pin.IN, Pin.PULL_UP)
button_prev = Pin(15, Pin.IN, Pin.PULL_UP)

epd = EPD_2in13_V4_Landscape()


def count_pages():
    try:
        return len([f for f in os.listdir(PAGES_DIR) if f.startswith("page_")])
    except OSError:
        return 0


def load_page_number():
    try:
        with open(STATE_FILE) as f:
            return int(f.read().strip())
    except (OSError, ValueError):
        return 0


def save_page_number(n):
    with open(STATE_FILE, "w") as f:
        f.write(str(n))


def show_page(n):
    path = "{}/page_{:04d}.txt".format(PAGES_DIR, n)
    try:
        with open(path) as f:
            lines = f.read().split("\n")
    except OSError:
        lines = ["(missing page file)"]

    epd.fill(0xff)
    y = 6
    for line in lines:
        epd.text(line, 0, y, 0x00)
        y += 8

    footer = "{}/{}".format(n + 1, total_pages)
    footer_x = SCREEN_W - (len(footer) * 8) - 2
    epd.text(footer, footer_x, SCREEN_H - 10, 0x00)

    epd.displayPartial(epd.buffer)


total_pages = count_pages()
current_page = load_page_number()
if current_page >= total_pages:
    current_page = 0

if total_pages == 0:
    epd.fill(0xff)
    epd.text("No pages found.", 0, 0, 0x00)
    epd.text("Copy /pages onto", 0, 10, 0x00)
    epd.text("the Pico first.", 0, 20, 0x00)
    epd.display(epd.buffer)
else:
    show_page(current_page)

print("Reader ready -", total_pages, "pages, starting at", current_page)

while True:
    if total_pages > 0:
        if button_next.value() == 0:
            if current_page < total_pages - 1:
                current_page += 1
                show_page(current_page)
                save_page_number(current_page)
            utime.sleep_ms(300)

        if button_prev.value() == 0:
            if current_page > 0:
                current_page -= 1
                show_page(current_page)
                save_page_number(current_page)
            utime.sleep_ms(300)

    utime.sleep_ms(50)
