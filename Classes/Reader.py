import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

class Reader():
    
    def __init__(self):
        self.reader = SimpleMFRC522()

    def read(self):
        self.id = self.reader.read_id()
        return self.id

    def __del__(self):
        GPIO.cleanup()