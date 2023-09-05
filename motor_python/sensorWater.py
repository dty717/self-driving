import digitalio
import board 
import time
import analogio
import board
import pwmio
from adafruit_motor import motor


led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

PIN_MOTOR_A = board.GP0  # pick any pwm pins on their own channels
PIN_MOTOR_B = board.GP1
# DC motor setup
# DC Motors generate electrical noise when running that can reset the microcontroller in extreme
# cases. A capacitor can be used to help prevent this.
pwm_motor_a = pwmio.PWMOut(PIN_MOTOR_A, frequency=50)
pwm_motor_b = pwmio.PWMOut(PIN_MOTOR_B, frequency=50)
motor = motor.DCMotor(pwm_motor_a, pwm_motor_b)

# motor.throttle

lowLevelADC = analogio.AnalogIn(board.A2)
highLevelADC = analogio.AnalogIn(board.A1)


def getLowLevelVoltage():
    return lowLevelADC.value / 65535 * 3.3*2

def getHighLevelVoltage():
    return highLevelADC.value / 65535 * 3.3*2


lowLevelThreshold = 3.5
highLevelThreshold = 3.1
isRunning = False


while True:
    (highLevelVoltage,lowLevelVoltage)=(getHighLevelVoltage(),getLowLevelVoltage())
    print((lowLevelVoltage,highLevelVoltage))
    time.sleep(0.1)
    if isRunning:
        if lowLevelVoltage > lowLevelThreshold and highLevelVoltage < highLevelThreshold:
            isRunning = False
            motor.throttle = 0
            led.value = 1
        else:
            led.value = not led.value
    else:
        if highLevelVoltage >= highLevelThreshold:
            isRunning = True
            motor.throttle = 1
            led.value = 1
        elif lowLevelVoltage < lowLevelThreshold:
            led.value = 1
        else:
            led.value = 0
    time.sleep(0.1)