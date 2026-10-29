# Altoids Tin E-Reader

A pocket-sized e-book reader built from a Raspberry Pi Pico W, a 2.13" e-ink display, and two buttons, all squeezed into an Altoids tin. It reads plain-text "pages" off the Pico's flash, remembers where you left off, and flips pages with a button press.

The demo book is *Fahrenheit 451*, split into 907 pages.

## How it works

E-ink screens are slow and the Pico's memory is tiny, so the heavy lifting happens on your PC ahead of time:

1. **`pdf_to_pages.py`** (runs on your PC) pulls the text out of a PDF, swaps smart quotes/dashes/ligatures for plain ASCII (the Pico's built-in font can't draw anything else), word-wraps it to 28 characters per line, and writes one `page_XXXX.txt` file per screen (13 lines each).
2. **`main.py`** (runs on the Pico) loads one page file at a time, draws it on the display, and listens for button presses. The current page number is saved to `/last_page.txt` so it resumes after power-off.

## Hardware

- Raspberry Pi Pico W
- 2.13" e-ink display (Waveshare-style V4 driver, 250x122 landscape)
- 2 push buttons
- Altoids tin (or any tin you like)

### Buttons

| Button | Pico pin | Action        |
|--------|----------|---------------|
| Next   | GP14     | Next page     |
| Prev   | GP15     | Previous page |

Wire each button between its GPIO pin and GND. The code uses the internal pull-up resistors, so no external resistors are needed.

## Repo contents

| File               | What it does                                            |
|--------------------|---------------------------------------------------------|
| `main.py`          | MicroPython reader program for the Pico                 |
| `pdf_to_pages.py`  | PC-side script that turns a PDF into page files         |
| `.gitignore`       | Keeps books and generated pages out of the repo         |

> **Not included:** the `epd2in13v4.py` display driver. Grab the 2.13" V4 e-paper MicroPython driver for your display and copy it onto the Pico alongside `main.py`.
>
> **Also not included:** book files. See the note on copyright below.

## Setup

### 1. Convert a book to pages (on your PC)

```bash
pip install pypdf
python pdf_to_pages.py yourbook.pdf pages/
```

This creates a `pages/` folder full of `page_0000.txt`, `page_0001.txt`, and so on.

### 2. Put everything on the Pico

Flash MicroPython onto the Pico W, then copy these to it (Thonny, `mpremote`, or rshell all work):

- `main.py`
- `epd2in13v4.py` (the display driver)
- the whole `pages/` folder, copied to `/pages` on the Pico

Example with `mpremote`:

```bash
mpremote cp epd2in13v4.py :
mpremote cp -r pages :
mpremote cp main.py :
```

### 3. Read

Power it up. It shows the page you left off on (or page 1 the first time). Press **Next** and **Prev** to flip pages.

## Tweaking

- **Page size:** `CHARS_PER_LINE` and `LINES_PER_PAGE` at the top of `pdf_to_pages.py`. If you change them, re-run the script and re-copy the pages.
- **Debounce / button feel:** the `utime.sleep_ms(300)` after each press in `main.py`.
- **Different display:** change `SCREEN_W`, `SCREEN_H`, and the driver import in `main.py`.

## Limitations

- ASCII only. Accented letters and other non-ASCII characters are dropped.
- PDF text extraction can be messy (headers, footers, page numbers, odd line breaks) depending on the source PDF.
- Page files are loaded from flash one at a time, so there's no real "jump to page" yet.

## Copyright note

The demo book is still under copyright. Don't commit book PDFs or generated page files to a public repo. Bring your own book (public-domain titles from [Project Gutenberg](https://www.gutenberg.org/) work great).

## Ideas for later

- Jump-to-page / bookmarks
- Battery power and sleep mode
- Larger font
- Multiple books with a menu