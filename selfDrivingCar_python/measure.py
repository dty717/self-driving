
import time
import analogio
import board
import microcontroller

adc4 = analogio.AnalogIn(board.A3)
adc3 = analogio.AnalogIn(board.A1)
adc2 = analogio.AnalogIn(board.A2)
adc1 = analogio.AnalogIn(board.A0)


def getSelfVoltage():
    return adc4.value / 65535 * 3.3 * 3


def getVoltage():
    return adc3.value / 65535 * 3.3 * (3 + 22.1) / 3 * (3.3/3.388)


def getSolarVoltage():
    return adc1.value / 65535 * 3.3 * (20 + 294) / 20 * (3.3/3.82)


def getTemperature():
    return microcontroller.cpu.temperature

# 3.3v        33538
# 3.7v~4.1v  ~40956
# 5v          51833


initWCS1800Val = 33538
K_WCS1800 = 60 / 5 * 3.3


def initWCS1800(adc, times=1000):
    global initWCS1800Val
    initWCS1800SumTimes = times
    initWCS1800Val = 0
    while True:
        initWCS1800Val += adc.value
        initWCS1800SumTimes -= 1
        if initWCS1800SumTimes <= 0:
            break
    initWCS1800Val = initWCS1800Val / times
    return initWCS1800Val


def currentWCS1800(adc, times=1):
    global initWCS1800Val
    val = 0
    _times = times
    while _times > 0:
        val += adc.value
        _times -= 1
    return -(val/times - initWCS1800Val) / 65535 * 3.3 / K_WCS1800*1000

# initWCS1800Val = initWCS1800(adc2)

# while True:
#     (getSolarVoltage(),)
#     time.sleep(0.05)


def getMeasurement():
    return ("temperature:"+str(getTemperature())+",self voltage:"+str(getSelfVoltage()) + ",solar voltage:"+str(getSolarVoltage())+",output voltage:"+str(getVoltage()) + ",output current:" + str(currentWCS1800(adc2, 1000)))
