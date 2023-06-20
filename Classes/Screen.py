from lcd_api import LcdApi
from i2c_lcd import I2cLcd

class Screen():

    def __init__(self):
        self.lcd = I2cLcd(1, 0x27, 2, 16)

    def write(self, text, line=0):
        self.lcd.move_to(0, line)
        self.lcd.putstr(text)

    def clear(self):
        self.lcd.clear()

    def __del__(self):
        self.lcd.clear()

    def enableScreen(self):
        self.lcd.display_on()

    def disableScreen(self):
        self.lcd.display_off()