import RPi.GPIO as GPIO

DATA = 20
CLK = 21
LE = 22
OE_PINS = (23, 24, 25)
SW1 = 26
SW2 = 27
LED_COUNT = 48
PRESSED_LEVEL = GPIO.LOW


def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in (DATA, CLK, LE):
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
    for pin in OE_PINS:
        GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(SW1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(SW2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    show(0)
    for pin in OE_PINS:
        GPIO.output(pin, GPIO.LOW)


def _pulse(pin):
    GPIO.output(pin, GPIO.HIGH)
    GPIO.output(pin, GPIO.LOW)


def show(state):
    for bit in reversed(range(LED_COUNT)):
        GPIO.output(DATA, (state >> bit) & 1)
        _pulse(CLK)
    _pulse(LE)


def is_pressed(button):
    return GPIO.input(button) == PRESSED_LEVEL


def cleanup():
    GPIO.output(CLK, GPIO.LOW)
    GPIO.output(LE, GPIO.LOW)
    show(0)
    for pin in OE_PINS:
        GPIO.output(pin, GPIO.HIGH)
    GPIO.cleanup((SW1, SW2))
