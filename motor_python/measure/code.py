

# 在这里写上你的代码 :-)

# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Essentials UART Serial example"""
import board
import busio
import digitalio
import analogio
# pwm = pwmio.PWMOut(board.GP8)


import time
import board
import digitalio
import analogio
from adafruit_motor import stepper

# from adafruit_motor.a4998 import *

enPin = board.GP10
dirPin = board.GP1
plusePin = board.GP0

pluse = digitalio.DigitalInOut(plusePin)
dir = digitalio.DigitalInOut(dirPin)
en = digitalio.DigitalInOut(enPin)

pluse.direction = digitalio.Direction.OUTPUT
dir.direction = digitalio.Direction.OUTPUT
en.direction = digitalio.Direction.OUTPUT
isUsingA4998 = False 

if isUsingA4998:
    en.value = 0
else:
    en.switch_to_output()
    en.value = 0

DELAY = 0.01
STEPS = 200
DIRECTION = stepper.BACKWARD
STYLE = stepper.SINGLE

lastDelay = 0.01
lastSteps = 200
lastDirection = stepper.BACKWARD
LAST_STYLE = stepper.SINGLE

SHOWADC = False

opticalDownSwitch = analogio.AnalogIn(board.A2)
magnetism = analogio.AnalogIn(board.A1)
opticalUpSwitch = analogio.AnalogIn(board.A0)


opticalUpSwitchThreshold = (6832+672)/2
opticalDownSwitchThreshold = 31328/2

magnetismThreshold = 4200

lastShowCount = 0

stepsPerCircle = 400


class DeviceState:
    steps = 0
    onceMagnetismClosedStep = -1
    onceMagnetismClosedValue = -1
    onceMagnetismFarStep = -1
    onceMagnetismFarValue = -1
    onceOpticalUpSwitchAwayStep = -1
    onceOpticalUpSwitchAwayValue = -1
    onceOpticalUpSwitchInStep = -1
    onceOpticalUpSwitchInValue = -1
    onceOpticalDownSwitchAwayStep = -1
    onceOpticalDownSwitchAwayValue = -1
    onceOpticalDownSwitchInStep = -1
    onceOpticalDownSwitchInValue = -1
    def __init__(self):
        self.initMagnetismValue = magnetism.value
        self.initOpticalUpSwitchValue = opticalUpSwitch.value
        self.initOpticalDownSwitchValue = opticalDownSwitch.value
        if self.initMagnetismValue > magnetismThreshold:
            self.initMagnetismInfo = "Magnetism closed"
            self.onceMagnetismClosed = True
            self.onceMagnetismClosedValue = self.initMagnetismValue
            self.onceMagnetismClosedStep = 0
            self.onceMagnetismFar = False
        else:
            self.initMagnetismInfo = "Magnetism far"
            self.onceMagnetismClosed = False
            self.onceMagnetismFar = True
            self.onceMagnetismFarValue = self.initMagnetismValue
            self.onceMagnetismFarStep = 0
        if self.initOpticalUpSwitchValue < opticalUpSwitchThreshold:
            self.initOpticalUpSwitchInfo = "Optical up switch away"
            self.onceOpticalUpSwitchAway = True
            self.onceOpticalUpSwitchAwayValue = self.initOpticalUpSwitchValue
            self.onceOpticalUpSwitchAwayStep = 0
            self.onceOpticalUpSwitchIn = False
        else:
            self.initOpticalUpSwitchInfo = "Optical up switch in"
            self.onceOpticalUpSwitchAway = False
            self.onceOpticalUpSwitchIn = True
            self.onceOpticalUpSwitchInValue = self.initOpticalUpSwitchValue
            self.onceOpticalUpSwitchInStep = 0
        if self.initOpticalDownSwitchValue < opticalDownSwitchThreshold:
            self.initOpticalDownSwitchInfo = "Optical down switch away"
            self.onceOpticalDownSwitchAway = True
            self.onceOpticalDownSwitchAwayValue = self.initOpticalDownSwitchValue
            self.onceOpticalDownSwitchAwayStep = 0
            self.onceOpticalDownSwitchIn = False
        else:
            self.initOpticalDownSwitchInfo = "Optical down switch in"
            self.onceOpticalDownSwitchAway = False
            self.onceOpticalDownSwitchIn = True
            self.onceOpticalDownSwitchInValue = self.initOpticalDownSwitchValue
            self.onceOpticalDownSwitchInStep = 0        

    def __str__(self):
        return """steps = {}
initMagnetismValue = {}
initMagnetismInfo = {}
onceMagnetismClosed = {}
onceMagnetismClosedValue = {}
onceMagnetismClosedStep = {}
onceMagnetismFar = {}
onceMagnetismFarValue = {}
onceMagnetismFarStep = {}
initOpticalUpSwitchValue = {}
initOpticalUpSwitchInfo = {}
onceOpticalUpSwitchAway = {}
onceOpticalUpSwitchAwayValue = {}
onceOpticalUpSwitchAwayStep = {}
onceOpticalUpSwitchIn = {}
onceOpticalUpSwitchInValue = {}
onceOpticalUpSwitchInStep = {}

initOpticalDownSwitchValue = {}
initOpticalDownSwitchInfo = {}
onceOpticalDownSwitchAway = {}
onceOpticalDownSwitchAwayValue = {}
onceOpticalDownSwitchAwayStep = {}
onceOpticalDownSwitchIn = {}
onceOpticalDownSwitchInValue = {}
onceOpticalDownSwitchInStep = {}""".format(self.steps, self.initMagnetismValue, self.initMagnetismInfo, self.onceMagnetismClosed, self.onceMagnetismClosedValue, self.onceMagnetismClosedStep, self.onceMagnetismFar, self.onceMagnetismFarValue, self.onceMagnetismFarStep,
                                       self.initOpticalUpSwitchValue, self.initOpticalUpSwitchInfo, self.onceOpticalUpSwitchAway, self.onceOpticalUpSwitchAwayValue, self.onceOpticalUpSwitchAwayStep, self.onceOpticalUpSwitchIn, self.onceOpticalUpSwitchInValue, self.onceOpticalUpSwitchInStep,
                                       self.initOpticalDownSwitchValue, self.initOpticalDownSwitchInfo, self.onceOpticalDownSwitchAway, self.onceOpticalDownSwitchAwayValue, self.onceOpticalDownSwitchAwayStep, self.onceOpticalDownSwitchIn, self.onceOpticalDownSwitchInValue, self.onceOpticalDownSwitchInStep)


deviceState = DeviceState()
lastDeviceState = DeviceState()

pluseValue = True

def onestep(interrupt):
    global deviceState,pluseValue
    if handleData(interrupt):
        return True
    else:
        if isUsingA4998:
            pluse.value = not pluse.value
        else:
            pluseValue = not pluseValue
            if pluseValue:
                # pluse.value = 1
                pluse.switch_to_input()
            else:
                pluse.switch_to_output()
                pluse.value = 0
        deviceState.steps += 1
        return False


def run(steps=STEPS, delay=DELAY, direction=DIRECTION, style=STYLE, interrupt=lambda arg1, arg2,arg3: False):
    global lastDelay
    global lastDirection
    global lastSteps
    global LAST_STYLE
    lastSteps = steps
    lastDelay = delay
    lastDirection = direction
    LAST_STYLE = style
    if isUsingA4998:
        en.value = 1
    else:
        # en.value = 1
        en.switch_to_input()
    if direction == stepper.BACKWARD:
        if isUsingA4998:
            dir.value = 1
        else:
            # dir.value = 1
            dir.switch_to_input()
    else:
        if isUsingA4998:
            dir.value = 0
        else:
            dir.switch_to_output()
            dir.value = 0
    print("steps:"+str(steps))
    for step in range(steps):
        if onestep(interrupt):
            break
        time.sleep(delay)
    if isUsingA4998:
        en.value = 0
    else:
        en.switch_to_output()
        en.value = 0
    # resetDeviceState()


def oppositeDirection(direction=DIRECTION):
    if(direction == stepper.FORWARD):
        return stepper.BACKWARD
    else:
        return stepper.FORWARD

# run(steps=6000,interrupt=detectOpticalUpSwitchAway)


def redo(steps=lastSteps, delay=lastDelay, interrupt=lambda arg1, arg2,arg3: False):
    if isUsingA4998:
        en.value = 1
    else:
        # en.value = 1
        en.switch_to_input()
    if oppositeDirection(lastDirection) == stepper.BACKWARD:
        if isUsingA4998:
            dir.value = 1
        else:
            # dir.value = 1
            dir.switch_to_input()
    else:
        if isUsingA4998:
            dir.value = 0
        else:
            dir.switch_to_output()
            dir.value = 0
    for step in range(steps):
        if onestep(interrupt):
            break
        time.sleep(delay)
    if isUsingA4998:
        en.value = 0
    else:
        en.switch_to_output()
        en.value = 0
    # resetDeviceState()

# # For most CircuitPython boards:
# a = digitalio.DigitalInOut(board.GP0)
# # For QT Py M0:
# # led = digitalio.DigitalInOut(board.SCK)
# a.direction = digitalio.Direction.OUTPUT

# # For most CircuitPython boards:
# b = digitalio.DigitalInOut(board.GP1)
# # For QT Py M0:
# # led = digitalio.DigitalInOut(board.SCK)
# b.direction = digitalio.Direction.OUTPUT


def resetDeviceState():
    global deviceState, lastDeviceState
    lastDeviceState.initMagnetismValue = deviceState.initMagnetismValue
    lastDeviceState.initMagnetismInfo = deviceState.initMagnetismInfo
    lastDeviceState.onceMagnetismClosed = deviceState.onceMagnetismClosed
    lastDeviceState.onceMagnetismClosedValue = deviceState.onceMagnetismClosedValue
    lastDeviceState.onceMagnetismClosedStep = deviceState.onceMagnetismClosedStep
    lastDeviceState.onceMagnetismFar = deviceState.onceMagnetismFar
    lastDeviceState.onceMagnetismFarValue = deviceState.onceMagnetismFarValue
    lastDeviceState.onceMagnetismFarStep = deviceState.onceMagnetismFarStep
    lastDeviceState.initOpticalUpSwitchValue = deviceState.initOpticalUpSwitchValue
    lastDeviceState.initOpticalUpSwitchInfo = deviceState.initOpticalUpSwitchInfo
    lastDeviceState.onceOpticalUpSwitchAway = deviceState.onceOpticalUpSwitchAway
    lastDeviceState.onceOpticalUpSwitchAwayStep = deviceState.onceOpticalUpSwitchAwayStep
    lastDeviceState.onceOpticalUpSwitchAwayValue = deviceState.onceOpticalUpSwitchAwayValue
    lastDeviceState.onceOpticalUpSwitchIn = deviceState.onceOpticalUpSwitchIn
    lastDeviceState.onceOpticalUpSwitchInValue = deviceState.onceOpticalUpSwitchInValue
    lastDeviceState.onceOpticalUpSwitchInStep = deviceState.onceOpticalUpSwitchInStep

    lastDeviceState.initOpticalDownSwitchValue = deviceState.initOpticalDownSwitchValue
    lastDeviceState.initOpticalDownSwitchInfo = deviceState.initOpticalDownSwitchInfo
    lastDeviceState.onceOpticalDownSwitchAway = deviceState.onceOpticalDownSwitchAway
    lastDeviceState.onceOpticalDownSwitchAwayStep = deviceState.onceOpticalDownSwitchAwayStep
    lastDeviceState.onceOpticalDownSwitchAwayValue = deviceState.onceOpticalDownSwitchAwayValue
    lastDeviceState.onceOpticalDownSwitchIn = deviceState.onceOpticalDownSwitchIn
    lastDeviceState.onceOpticalDownSwitchInValue = deviceState.onceOpticalDownSwitchInValue
    lastDeviceState.onceOpticalDownSwitchInStep = deviceState.onceOpticalDownSwitchInStep    
    lastDeviceState.steps = deviceState.steps
    #
    deviceState.initMagnetismValue = magnetism.value
    deviceState.initOpticalUpSwitchValue = opticalUpSwitch.value
    deviceState.initOpticalDownSwitchValue = opticalDownSwitch.value
    if deviceState.initMagnetismValue > magnetismThreshold:
        deviceState.initMagnetismInfo = "Magnetism closed"
        deviceState.onceMagnetismClosed = True
        deviceState.onceMagnetismClosedValue = deviceState.initMagnetismValue
        deviceState.onceMagnetismClosedStep = 0
        deviceState.onceMagnetismFar = False
        deviceState.onceMagnetismFarValue = -1
        deviceState.onceMagnetismFarStep = -1
    else:
        deviceState.initMagnetismInfo = "Magnetism far"
        deviceState.onceMagnetismClosed = False
        deviceState.onceMagnetismClosedValue = -1
        deviceState.onceMagnetismClosedStep = -1
        deviceState.onceMagnetismFar = True
        deviceState.onceMagnetismFarValue = deviceState.initMagnetismValue
        deviceState.onceMagnetismFarStep = 0
    if deviceState.initOpticalUpSwitchValue < opticalUpSwitchThreshold:
        deviceState.initOpticalUpSwitchInfo = "Optical Up switch away"
        deviceState.onceOpticalUpSwitchAway = True
        deviceState.onceOpticalUpSwitchAwayValue = deviceState.initOpticalUpSwitchValue
        deviceState.onceOpticalUpSwitchAwayStep = 0
        deviceState.onceOpticalUpSwitchIn = False
        deviceState.onceOpticalUpSwitchInValue = -1
        deviceState.onceOpticalUpSwitchInStep = -1
    else:
        deviceState.initOpticalUpSwitchInfo = "Optical Up switch in"
        deviceState.onceOpticalUpSwitchAway = False
        deviceState.onceOpticalUpSwitchAwayValue = -1
        deviceState.onceOpticalUpSwitchAwayStep = -1
        deviceState.onceOpticalUpSwitchIn = True
        deviceState.onceOpticalUpSwitchInValue = deviceState.initOpticalUpSwitchValue
        deviceState.onceOpticalUpSwitchInStep = 0
    if deviceState.initOpticalDownSwitchValue < opticalDownSwitchThreshold:
        deviceState.initOpticalDownSwitchInfo = "Optical Down switch away"
        deviceState.onceOpticalDownSwitchAway = True
        deviceState.onceOpticalDownSwitchAwayValue = deviceState.initOpticalDownSwitchValue
        deviceState.onceOpticalDownSwitchAwayStep = 0
        deviceState.onceOpticalDownSwitchIn = False
        deviceState.onceOpticalDownSwitchInValue = -1
        deviceState.onceOpticalDownSwitchInStep = -1
    else:
        deviceState.initOpticalDownSwitchInfo = "Optical Down switch in"
        deviceState.onceOpticalDownSwitchAway = False
        deviceState.onceOpticalDownSwitchAwayValue = -1
        deviceState.onceOpticalDownSwitchAwayStep = -1
        deviceState.onceOpticalDownSwitchIn = True
        deviceState.onceOpticalDownSwitchInValue = deviceState.initOpticalDownSwitchValue
        deviceState.onceOpticalDownSwitchInStep = 0
    deviceState.steps = 0


def showData(magnetismValue, OpticalUpSwitchValue,OpticalDownSwitchValue):
    global lastShowCount
    lastShowCount += 1
    if lastShowCount % 3 == 0:
        print(((magnetismValue, OpticalUpSwitchValue,OpticalDownSwitchValue)))
    if lastShowCount > 100000:
        lastShowCount = 0


def handleData(interrupt):
    global deviceState
    magnetismValue = 0
    OpticalUpSwitchValue = 0
    OpticalDownSwitchValue = 0
    for i in range(4):
        magnetismValue += magnetism.value/4
        OpticalUpSwitchValue += opticalUpSwitch.value/4
        OpticalDownSwitchValue += opticalDownSwitch.value/4
    if SHOWADC:
        showData(magnetismValue, OpticalUpSwitchValue,OpticalDownSwitchValue)
    if interrupt:
        if not deviceState.onceMagnetismClosed:
            if(magnetismValue < magnetismThreshold):
                pass
            else:
                deviceState.onceMagnetismClosed = True
                deviceState.onceMagnetismClosedValue = magnetismValue
                deviceState.onceMagnetismClosedStep = deviceState.steps
        elif not deviceState.onceMagnetismFar:
            if(magnetismValue < magnetismThreshold):
                deviceState.onceMagnetismFar = True
                deviceState.onceMagnetismFarValue = magnetismValue
                deviceState.onceMagnetismFarStep = deviceState.steps
            else:
                pass
        if not deviceState.onceOpticalUpSwitchIn:
            if(OpticalUpSwitchValue > opticalUpSwitchThreshold):
                # valid = False
                # for i in range(3):
                #     if OpticalUpSwitch.value < OpticalUpSwitchThreshold:
                #         pass
                deviceState.onceOpticalUpSwitchIn = True
                deviceState.onceOpticalUpSwitchInValue = OpticalUpSwitchValue
                deviceState.onceOpticalUpSwitchInStep = deviceState.steps
            else:
                pass
        elif not deviceState.onceOpticalUpSwitchAway:
            if(OpticalUpSwitchValue > opticalUpSwitchThreshold):
                pass
            else:
                deviceState.onceOpticalUpSwitchAway = True
                deviceState.onceOpticalUpSwitchAwayValue = OpticalUpSwitchValue
                deviceState.onceOpticalUpSwitchAwayStep = deviceState.steps
        
        if not deviceState.onceOpticalDownSwitchIn:
            if(OpticalDownSwitchValue > opticalDownSwitchThreshold):
                # valid = False
                # for i in range(3):
                #     if OpticalDownSwitch.value < OpticalDownSwitchThreshold:
                #         pass
                deviceState.onceOpticalDownSwitchIn = True
                deviceState.onceOpticalDownSwitchInValue = OpticalDownSwitchValue
                deviceState.onceOpticalDownSwitchInStep = deviceState.steps
            else:
                pass
        elif not deviceState.onceOpticalDownSwitchAway:
            if(OpticalDownSwitchValue > opticalDownSwitchThreshold):
                pass
            else:
                deviceState.onceOpticalDownSwitchAway = True
                deviceState.onceOpticalDownSwitchAwayValue = OpticalDownSwitchValue
                deviceState.onceOpticalDownSwitchAwayStep = deviceState.steps
        return interrupt(magnetismValue, OpticalUpSwitchValue,OpticalDownSwitchValue)
    else:
        return False


def showState():
    if(magnetism.value < magnetismThreshold):
        print("Magnetism is weak,so the hole is not close.")
    else:
        print("Magnetism is strong,so the hole is close.")
    if(opticalUpSwitch.value > opticalUpSwitchThreshold):
        print("Optical up switch light is close, so the pin is detect")
    else:
        print("Optical up switch light is open, so the pin is not detect")
    if(opticalDownSwitch.value > opticalDownSwitchThreshold):
        print("Optical down switch light is close, so the pin is detect")
    else:
        print("Optical down switch light is open, so the pin is not detect")

def detectMagnetismHoleClose(magnetismValue, OpticalUpSwitchValue,OpticalDownSwitchValue):
    if(magnetismValue < magnetismThreshold):
        return False
    else:
        return True


def detectMagnetismDetectHoleAndLeave(magnetismValue, OpticalUpSwitchValue,OpticalDownSwitchValue):
    global deviceState
    if deviceState.onceMagnetismClosed:
        if(magnetismValue < magnetismThreshold):
            return True
        else:
            return False


DetectHoleAndMoveSteps = stepsPerCircle*2


def detectMagnetismDetectHoleAndMove(magnetismValue, OpticalUpSwitchValue,OpticalDownSwitchValue):
    global deviceState
    if deviceState.onceMagnetismClosed:
        if(deviceState.steps > deviceState.onceMagnetismClosedStep + DetectHoleAndMoveSteps):
            return True
        else:
            return False


def detectOpticalUpSwitchIn(magnetismValue, OpticalUpSwitchValue,OpticalDownSwitchValue):
    global deviceState
    if deviceState.onceOpticalUpSwitchIn:
        return True
    else:
        return False


def detectOpticalUpSwitchAway(magnetismValue, OpticalUpSwitchValue,OpticalDownSwitchValue):
    global deviceState
    if deviceState.onceOpticalUpSwitchAway:
        return True
    else:
        return False


def detectOpticalDownSwitchIn(magnetismValue, OpticalUpSwitchValue,OpticalDownSwitchValue):
    global deviceState
    if deviceState.onceOpticalDownSwitchIn:
        return True
    else:
        return False



## enter sample
# redo(steps=30000, interrupt=detectMagnetismDetectHoleAndMove, delay=DELAY)
# run(steps=3000,interrupt=detectOpticalUpSwitchIn)

# OpticalUpSwitchThreshold = 1060
#
# OpticalUpSwitchThreshold = 760

# redo(steps = 6*stepsPerCircle,interrupt=detectOpticalDownSwitchIn)


# while True:
#     time.sleep(0.05)
#     (OpticalUpSwitch.value,)
