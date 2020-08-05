import time

try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except Exception as e:
    print(e)
    pass

from modules import cbpi
from modules.core.hardware import ActorBase, SensorPassive, SensorActive
from modules.core.props import Property


class RemoteSwitch(object):
    repeat = 10
    pulselength = 300
    GPIOMode = GPIO.BCM

    def __init__(self, key=[1, 1, 1, 1, 1], pin=4):
        
        self.pin = pin
        self.key = key
        GPIO.setmode(self.GPIOMode)
        GPIO.setup(self.pin, GPIO.OUT)

    def switchOn(self, device):
        self._switch(device,GPIO.HIGH)

    def switchOff(self, device):
        self._switch(device,GPIO.LOW)

    def _switch(self, device, switch):
        self.bit = [142, 142, 142, 142, 142, 142, 142, 142, 142, 142, 142, 136, 128, 0, 0, 0]

        for t in range(5):
            if self.key[t]:
                self.bit[t] = 136
        x = 1
        for i in range(1, 6):
            if device & x > 0:
                self.bit[4 + i] = 136
            x = x << 1

        if switch == GPIO.HIGH:
            self.bit[10] = 136
            self.bit[11] = 142

        bangs = []
        for y in range(16):
            x = 128
            for i in range(1, 9):
                b = (self.bit[y] & x > 0) and GPIO.HIGH or GPIO.LOW
                bangs.append(b)
                x = x >> 1

        GPIO.output(self.pin, GPIO.LOW)
        for z in range(self.repeat):
            for b in bangs:
                GPIO.output(self.pin, b)
                time.sleep(self.pulselength / 1000000.)

@cbpi.actor
class Socket433MHz(ActorBase):
    socket = Property.Select("socket", options=[1, 2, 3, 4, 5, 6])

    @classmethod
    def init_global(cls):
        default_key = [1, 0, 0, 0, 1]
        default_pin = 17
        cls.device = RemoteSwitch(key=default_key, pin=default_pin)

    def on(self, power=100):
        self.device.switchOn(int(self.socket))

    def off(self):
        self.device.switchOff(int(self.socket))


