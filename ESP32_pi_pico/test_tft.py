"""
hello.py
    Writes "Hello!" in random colors at random locations on the display.
"""
import random
from machine import Pin, SPI
import time
import st7789py as st7789

# Choose a font

# from romfonts import vga1_8x8 as font
# from romfonts import vga2_8x8 as font
# from romfonts import vga1_8x16 as font
# from romfonts import vga2_8x16 as font
# from romfonts import vga1_16x16 as font
# from romfonts import vga1_bold_16x16 as font
# from romfonts import vga2_16x16 as font
# from romfonts import vga2_bold_16x16 as font
# from romfonts import vga1_16x32 as font
# from romfonts import vga1_bold_16x32 as font
# from romfonts import vga2_16x32 as font
import vga1_bold_16x32 as font

import tft_config


lcd_pow = Pin(22, Pin.OUT)
lcd_pow.off()
time.sleep(1)
lcd_pow.on()


def main():

    #tft = tft_config.config
    spi = SPI(0,
        baudrate=62500000,
        polarity=1,
        phase=1,
        sck=Pin(2, Pin.OUT),
        mosi=Pin(3, Pin.OUT),
        miso=None)

    tft = st7789.ST7789(
        spi,
        135,
        240,
        cs=Pin(5, Pin.OUT),
        dc=Pin(1, Pin.OUT),
        backlight=Pin(4, Pin.OUT),
        rotation=1)
    
    while True:
        for rotation in range(4):
            tft.rotation(rotation)
            tft.fill(0)
            col_max = tft.width - font.WIDTH*6
            row_max = tft.height - font.HEIGHT

            for _ in range(100):
                tft.text(
                    font,
                    "Hello!",
                    random.randint(0, col_max),
                    random.randint(0, row_max),
                    st7789.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8)),
                    st7789.color565(
                        random.getrandbits(8),
                        random.getrandbits(8),
                        random.getrandbits(8))
                )


main()