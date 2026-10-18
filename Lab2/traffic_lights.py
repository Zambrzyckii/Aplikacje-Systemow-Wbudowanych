import RPi.GPIO as GPIO
from time import monotonic, sleep

DATA = 20
CLK = 21
LE = 22
OE_PINS = (23, 24, 25)
SW1 = 26
SW2 = 27
LED_COUNT = 48
PRESSED_LEVEL = GPIO.LOW
POLL_INTERVAL = 0.05

NORTH_SOUTH_HEADS = (
    {"red": 16, "yellow": 17, "green": 18, "arrow": 19},
    {"red": 30, "yellow": 29, "green": 28},
    {"red": 32, "yellow": 33, "green": 34, "arrow": 35},
    {"red": 47, "yellow": 46, "green": 45},
)

WEST_EAST_HEADS = (
    {"red": 0, "yellow": 1, "green": 2, "arrow": 3},
    {"red": 8, "yellow": 9, "green": 10, "arrow": 11},
)

NORTH_CROSSWALK = (
    {"red": 20, "green": 21},
    {"red": 22, "green": 23},
    {"red": 24, "green": 25},
    {"red": 27, "green": 26},
)

SOUTH_CROSSWALK = (
    {"red": 44, "green": 43},
    {"red": 38, "green": 39},
    {"red": 41, "green": 42},
    {"red": 36, "green": 37},
)

WEST_CROSSWALK = (
    {"red": 15, "green": 14},
    {"red": 12, "green": 13},
)

EAST_CROSSWALK = (
    {"red": 4, "green": 5},
    {"red": 7, "green": 6},
)

PHASES = (
    ("red", "red", False, False, 2),
    ("red_yellow", "red", False, False, 1),
    ("green", "red", True, False, 5),
    ("green", "red", False, False, 2),
    ("green", "red", False, True, 3),
    ("yellow", "red", False, False, 3),
    ("red", "red", False, False, 1),
    ("red", "red_yellow", False, False, 1),
    ("red", "green", True, False, 4),
    ("red", "green", False, False, 2),
    ("red", "green", False, True, 2),
    ("red", "yellow", False, False, 3),
)
ASPECT_COLORS = {
    "red": ("red",),
    "red_yellow": ("red", "yellow"),
    "green": ("green",),
    "yellow": ("yellow",),
}
BUTTONS = (
    (SW1, "east"),
    (SW2, "west"),
)


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


def bits(groups, *colors):
    state = 0
    for group in groups:
        for color in colors:
            if color in group:
                state |= 1 << group[color]
    return state


def frame(north_south, west_east, walk, arrows, served):
    state = bits(NORTH_SOUTH_HEADS, *ASPECT_COLORS[north_south])
    state |= bits(WEST_EAST_HEADS, *ASPECT_COLORS[west_east])

    north_south_walk = walk and west_east == "green"
    state |= bits(NORTH_CROSSWALK + SOUTH_CROSSWALK, "green" if north_south_walk else "red")
    for side, crosswalk in (("west", WEST_CROSSWALK), ("east", EAST_CROSSWALK)):
        side_walk = walk and north_south == "green" and side in served
        state |= bits(crosswalk, "green" if side_walk else "red")

    if arrows and not walk:
        if north_south == "green":
            state |= bits(WEST_EAST_HEADS, "arrow")
        if west_east == "green":
            state |= bits(NORTH_SOUTH_HEADS, "arrow")
    return state


def wait(duration, requests, was_pressed):
    deadline = monotonic() + duration
    while monotonic() < deadline:
        for pin, side in BUTTONS:
            pressed = is_pressed(pin)
            if pressed and not was_pressed[pin]:
                requests.add(side)
                print(f"Pedestrian request: {side}")
            was_pressed[pin] = pressed
        sleep(POLL_INTERVAL)


def main():
    setup()
    requests = set()
    served = set()
    was_pressed = {pin: is_pressed(pin) for pin, _ in BUTTONS}
    try:
        while True:
            for number, (north_south, west_east, walk, arrows, duration) in enumerate(PHASES, start=1):
                if walk and north_south == "green":
                    served = requests
                    requests = set()
                print(f"Phase {number}: north-south {north_south}, west-east {west_east}, walk {walk}, arrows {arrows}")
                show(frame(north_south, west_east, walk, arrows, served))
                wait(duration, requests, was_pressed)
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        cleanup()


if __name__ == "__main__":
    main()
