import time
import board
import digitalio
from adafruit_motor import stepper

DELAY = 0.01
STEPS = 200
DIRECTION = stepper.BACKWARD
STYLE = stepper.SINGLE

LAST_DELAY = 0.01
LAST_STEPS = 200
LAST_DIRECTION = stepper.BACKWARD
LAST_STYLE = stepper.SINGLE

A1 = board.GP9
A2 = board.GP10
B1 = board.GP11
B2 = board.GP12

# You can use any available GPIO pin on both a microcontroller and a Raspberry Pi.
# The following pins are simply a suggestion. If you use different pins, update
# the following code to use your chosen pins.

# To use with CircuitPython and a microcontroller:
coils = (
    digitalio.DigitalInOut(A1),  # A1
    digitalio.DigitalInOut(A2),  # A2
    digitalio.DigitalInOut(B1),  # B1
    digitalio.DigitalInOut(B2),  # B2
)

for coil in coils:
    coil.direction = digitalio.Direction.OUTPUT

motor = stepper.StepperMotor(
    coils[0], coils[1], coils[2], coils[3], microsteps=None)

def run(steps=STEPS, delay=DELAY, direction=DIRECTION, style=STYLE):
    global LAST_DELAY
    global LAST_DIRECTION
    global LAST_STEPS
    global LAST_STYLE
    LAST_STEPS = steps
    LAST_DELAY = delay
    LAST_DIRECTION = direction
    LAST_STYLE = style
    for step in range(steps):
        motor.onestep(direction=direction, style=style)
        time.sleep(delay)
    motor.release()


def oppositeDirection(direction=DIRECTION):
    if(direction == stepper.FORWARD):
        return stepper.BACKWARD
    else:
        return stepper.FORWARD


def redo():
    for step in range(LAST_STEPS):
        motor.onestep(direction=oppositeDirection(LAST_DIRECTION), style=LAST_DIRECTION)
        time.sleep(LAST_DELAY)
    motor.release()
