from time import monotonic, sleep

import intersection
import layout

POLL_INTERVAL = 0.05
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
    (intersection.SW1, "east"),
    (intersection.SW2, "west"),
)


def bits(groups, *colors):
    state = 0
    for group in groups:
        for color in colors:
            if color in group:
                state |= 1 << group[color]
    return state


def frame(north_south, west_east, walk, arrows, served):
    state = bits(layout.NORTH_SOUTH_HEADS, *ASPECT_COLORS[north_south])
    state |= bits(layout.WEST_EAST_HEADS, *ASPECT_COLORS[west_east])

    north_south_walk = walk and west_east == "green"
    state |= bits(layout.NORTH_CROSSWALK + layout.SOUTH_CROSSWALK, "green" if north_south_walk else "red")
    for side, crosswalk in (("west", layout.WEST_CROSSWALK), ("east", layout.EAST_CROSSWALK)):
        side_walk = walk and north_south == "green" and side in served
        state |= bits(crosswalk, "green" if side_walk else "red")

    if arrows and not walk:
        if north_south == "green":
            state |= bits(layout.WEST_EAST_HEADS, "arrow")
        if west_east == "green":
            state |= bits(layout.NORTH_SOUTH_HEADS, "arrow")
    return state


def wait(duration, requests, was_pressed):
    deadline = monotonic() + duration
    while monotonic() < deadline:
        for pin, side in BUTTONS:
            pressed = intersection.is_pressed(pin)
            if pressed and not was_pressed[pin]:
                requests.add(side)
                print(f"Pedestrian request: {side}")
            was_pressed[pin] = pressed
        sleep(POLL_INTERVAL)


def main():
    intersection.setup()
    requests = set()
    served = set()
    was_pressed = {pin: intersection.is_pressed(pin) for pin, _ in BUTTONS}
    try:
        while True:
            for number, (north_south, west_east, walk, arrows, duration) in enumerate(PHASES, start=1):
                if walk and north_south == "green":
                    served = requests
                    requests = set()
                print(f"Phase {number}: north-south {north_south}, west-east {west_east}, walk {walk}, arrows {arrows}")
                intersection.show(frame(north_south, west_east, walk, arrows, served))
                wait(duration, requests, was_pressed)
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        intersection.cleanup()


if __name__ == "__main__":
    main()
