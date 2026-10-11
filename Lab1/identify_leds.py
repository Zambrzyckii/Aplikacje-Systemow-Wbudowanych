from time import sleep

import intersection

POLL_INTERVAL = 0.05
BUTTONS = (
    ("SW1", intersection.SW1, 1),
    ("SW2", intersection.SW2, -1),
)


def light(bit):
    intersection.show(1 << bit)
    print(f"LED bit {bit}")


def main():
    intersection.setup()
    current = 0
    light(current)
    was_pressed = {name: intersection.is_pressed(pin) for name, pin, _ in BUTTONS}
    try:
        while True:
            for name, pin, step in BUTTONS:
                pressed = intersection.is_pressed(pin)
                if pressed != was_pressed[name]:
                    print(f"{name} {'pressed' if pressed else 'released'}")
                    if pressed:
                        current = (current + step) % intersection.LED_COUNT
                        light(current)
                    was_pressed[name] = pressed
            sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("Stopped")
    finally:
        intersection.cleanup()


if __name__ == "__main__":
    main()
