import time
import board
import digitalio
import analogio
from adafruit_motor import stepper

# from adafruit_motor.a4998 import * 


enPin = board.GP6
dirPin = board.GP8
plusePin = board.GP7
adc1 = analogio.AnalogIn(board.A0)

pluse = digitalio.DigitalInOut(plusePin)  # A1
dir = digitalio.DigitalInOut(dirPin)  # A2
en = digitalio.DigitalInOut(enPin)  # B1

pluse.direction = digitalio.Direction.OUTPUT
dir.direction = digitalio.Direction.OUTPUT
en.direction = digitalio.Direction.OUTPUT


DELAY = 0.01
STEPS = 200
DIRECTION = stepper.BACKWARD
STYLE = stepper.SINGLE

LAST_DELAY = 0.01
LAST_STEPS = 200
LAST_DIRECTION = stepper.BACKWARD
LAST_STYLE = stepper.SINGLE

SHOWADC = False


def onestep():
    pluse.value = not pluse.value
    if SHOWADC:
        print((adc1.value,))


def run(steps=STEPS, delay=DELAY, direction=DIRECTION, style=STYLE):
    global LAST_DELAY
    global LAST_DIRECTION
    global LAST_STEPS
    global LAST_STYLE
    LAST_STEPS = steps
    LAST_DELAY = delay
    LAST_DIRECTION = direction
    LAST_STYLE = style
    if direction == stepper.BACKWARD:
        dir.value = 1
    else:
        dir.value = 0
    for step in range(steps):
        onestep()
        time.sleep(delay)


def oppositeDirection(direction=DIRECTION):
    if(direction == stepper.FORWARD):
        return stepper.BACKWARD
    else:
        return stepper.FORWARD


def redo():
    if oppositeDirection(LAST_DIRECTION) == stepper.BACKWARD:
        dir.value = 1
    else:
        dir.value = 0
    for step in range(LAST_STEPS):
        onestep()
        time.sleep(LAST_DELAY)


# for num in range(100):
#     step.value = 1
#     time.sleep(0.01)
#     step.value = 0
#     time.sleep(0.01)
