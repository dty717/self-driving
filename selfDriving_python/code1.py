
import digitalio
import time
import re
import rtc
import board
import microcontroller
from microcontroller import watchdog
from watchdog import WatchDogMode
import analogio
import ov7670
import sim800_uart
import pioasm_rxuart
import command
import pwmio
from adafruit_motor import motor
import logger
import test
from config import initString, url, networkType, channel, port
# logInfo = open('/log/log.info','r')
# logInfoPage = (int(logInfo.read()) + 1) % 10
# logging = False
# error = 'error'
# try:
#     logFile = open('/log/' + str(logInfoPage)+'.log', 'w')
#     logging = True
# except Exception as e:
#     error = e.strerror
#     logging = False

adc3 = analogio.AnalogIn(board.A3)
def getVoltage():
    return adc3.value / 65535 *3.3 *3

def getTemperature():
    return microcontroller.cpu.temperature

led = digitalio.DigitalInOut(board.GP25)
led.direction = digitalio.Direction.OUTPUT
watchdog.timeout = 8  # Set a timeout of 2.5 seconds
watchdog.mode = WatchDogMode.RESET
index = 5
while index > 0:
    index -= 1
    led.value = led.value ^ 0b1
    time.sleep(1)

led.value = 0
watchdog.feed()

logger.initLog()

print("logging:"+str(logger.logging))

_isSIMBringUp = logger.isSIMBringUp()

# channel = 1
# networkType = "tcp"
# url = "155.138.195.23"
# port = 8808

clientSIM = sim800_uart.Client(channel, url, networkType, port, "", print)
simState = sim800_uart.SIMState([clientSIM])
commandState = command.Command()



PIN_MOTOR1_A = board.GP2  # pick any pwm pins on their own channels
PIN_MOTOR1_B = board.GP3
# DC motor setup
# DC Motors generate electrical noise when running that can reset the microcontroller in extreme
# cases. A capacitor can be used to help prevent this.
pwm_motor1_a = pwmio.PWMOut(PIN_MOTOR1_A, frequency=50)
pwm_motor1_b = pwmio.PWMOut(PIN_MOTOR1_B, frequency=50)
motor1 = motor.DCMotor(pwm_motor1_a, pwm_motor1_b)

PIN_MOTOR2_A = board.GP4  # pick any pwm pins on their own channels
PIN_MOTOR2_B = board.GP5
# DC motor setup
# DC Motors generate electrical noise when running that can reset the microcontroller in extreme
# cases. A capacitor can be used to help prevent this.
pwm_motor2_a = pwmio.PWMOut(PIN_MOTOR2_A, frequency=50)
pwm_motor2_b = pwmio.PWMOut(PIN_MOTOR2_B, frequency=50)
motor2 = motor.DCMotor(pwm_motor2_a, pwm_motor2_b)

ov7670.configOV7670()

heartbeatTimes = 20
heartbeatTime = heartbeatTimes
simRes = b''
simReceive = b''
startConnectionTimes = 10
startConnectionTime = startConnectionTimes
# uploadNum = 150
uploadNum = 730

def toHexString(bit):
    hexString = hex(bit)[2:]
    hexString = ("0000"+hexString)[-4:]
    return hexString

def uploadData(client, data, sendTimes=100):
    global heartbeatTime
    global simRes
    global simReceive
    simRes = b''
    simReceive = bytearray(500)
    if sim800_uart.sim_dataSending(client.channel, data):
        while sendTimes > 0:
            sendTimes -= 1
            sim800_uart.uart.readinto(simReceive)
            watchdog.feed()
            if simReceive != None:
                simRes = simRes + simReceive
                if simRes.find((str(client.channel)+', SEND OK\r\n').encode()) != -1:
                    client.sendState = True
                    heartbeatTime = heartbeatTimes
                    return True
                elif simRes.find((str(client.channel)+', CLOSED\r\n').encode()) != -1:
                    client.sendState = False
                    client.connectState = False
                    return False
                elif simRes.find(b'ERROR\r\n') != -1:
                    client.sendState = False
                    client.connectState = False
                    return False
                elif simRes.find('n\r\+RECEIVE,'.encode()) != -1:
                    receiveResult = sim800_uart.sim_dataReceiving(simReceive)
                    if receiveResult:
                        commandState.handleReceive(
                            receiveResult[0], receiveResult[1])
                        return False
                elif len(simRes) > 64:
                    simRes = simRes[-64:]
            watchdog.feed()
            # time.sleep(1)
            # watchdog.feed()
    else:
        for i in range(3):
            if sim800_uart.sim_startConnection(client.channel, client.networkType, client.url, client.port):
                watchdog.feed()
                time.sleep(4)
                watchdog.feed()
                return uploadData(client, data, sendTimes)
            watchdog.feed()
        client.connectState = False
        return False


def bitmapToHexString(bitmap, length, client):
    bitmapLen = bitmap.width * bitmap.height
    frameIndex = 0
    tem = b""
    watchdog.feed()
    uploadData(client,  ("img:"+str(bitmapLen)+","+str(length)).encode(), sendTimes=7000)
    for index in range(0, bitmapLen, length):
        frameIndex += 1
        # watchdog.feed()
        # time.sleep(5)
        watchdog.feed()
        tem = b""
        if index+length >= bitmapLen:
            for i in range(index, bitmapLen):
                tem += bytes([bitmap[i] >> 8, bitmap[i] & 0xff])
            if not uploadData(client,  ("#" + str(frameIndex) +
                       ":").encode()+tem, sendTimes=7000):
                return
        else:
            for i in range(index, length+index):
                tem += bytes([bitmap[i] >> 8, bitmap[i] & 0xff])
            if not uploadData(client,  ("#" + str(frameIndex) +
                       ":").encode()+tem, sendTimes=7000):
                return
    return


def uploadFile(filePath, client):
    buf = bytearray(500)
    try:
        file = open(filePath, 'r')
    except Exception as e:
        uploadData(client, str(e).encode(), sendTimes=7000)
        logger.log(str(e))
        return False
    fileReadLen = file.readinto(buf)
    if fileReadLen == 0:
        uploadData(client, b'[empty file]', sendTimes=7000)
        file.close()
        return True
    while True:
        watchdog.feed()
        if fileReadLen == 0:
            return True
        elif fileReadLen < 500:
            uploadData(client,  buf[0:fileReadLen], sendTimes=7000)
        else:
            uploadData(client,  buf, sendTimes=7000)
        fileReadLen = file.readinto(buf)


def uploadGPS(client):
    return uploadData(client, str(pioasm_rxuart.gpsData).encode())

def uploadHeartBeat(client):
    return uploadData(client, b'.')

def setUploadNum(num: int):
    global uploadNum
    uploadNum = num

bringUpWirelessConnectionTimes = 10
bringUpWirelessConnectionTime = bringUpWirelessConnectionTimes
bringUpWirelessConnectionState = False
localtime =time.localtime()
rtcTime = rtc.RTC()
closeSearchIndex = 0

def setupConnection():
    global _isSIMBringUp, simState, bringUpWirelessConnectionTime, bringUpWirelessConnectionTime,bringUpWirelessConnectionState
    time.sleep(1)
    if not _isSIMBringUp:
        if not simState.GPRSState:
            if sim800_uart.sim_checkIfConnected():
                watchdog.feed()
                simState.GPRSState = True
            else:
                watchdog.feed()
                return False
        # if sim800_uart.sim_resetIP():
        #     watchdog.feed()
        # else:
        #     watchdog.feed()
        #     continue
        if not simState.connectionMode:
            if sim800_uart.sim_enableMultiConnection():
                watchdog.feed()
                simState.connectionMode = 1
            else:
                watchdog.feed()
                if sim800_uart.sim_resetIP():
                    simState.reset()
                watchdog.feed()
                return False
        if not simState.pingState:
            if sim800_uart.sim_ping():
                watchdog.feed()
                time.sleep(3)
                watchdog.feed()
                simState.pingState = True
            else:
                watchdog.feed()
                if sim800_uart.sim_resetIP():
                    simState.reset()
                watchdog.feed()
                return False
        if not simState.bringUpWirelessConnectionState:
            bringUpWirelessConnectionTime = bringUpWirelessConnectionTimes
            sim800_uart.simpleHandle(sim800_uart.uart.read())
            logger.logSIMBringUp(True)
            sim800_uart.uart.write(b'AT+CIICR\r\n')
            time.sleep(0.1)
            logger.logSIMBringUp(False)
            res = sim800_uart.uart.readline()
            print(res)
            if res == b'AT+CIICR\r\r\n':
                time.sleep(5)
                # print(res)
            bringUpWirelessConnectionState = False
            while bringUpWirelessConnectionTime > 0:
                watchdog.feed()
                time.sleep(3)
                watchdog.feed()
                res = sim800_uart.uart.readline()
                print(res)
                bringUpWirelessConnectionTime -= 1
                if res == b'\r\n':
                    res = sim800_uart.uart.readline()
                    print(res)
                if res == b'OK\r\n':
                    bringUpWirelessConnectionState = True
                    break
                elif res == b'ERROR\r\n':
                    bringUpWirelessConnectionState = False
                    break
                # return False
            if bringUpWirelessConnectionState:
                watchdog.feed()
                time.sleep(3)
                watchdog.feed()
                simState.bringUpWirelessConnectionState = True
            else:
                watchdog.feed()
                time.sleep(3)
                watchdog.feed()
                if sim800_uart.sim_resetIP():
                    simState.reset()
                watchdog.feed()
                time.sleep(3)
                watchdog.feed()
                return False
    else:
        print("waiting for wireless connection bring up")
        for i in range(5):
            watchdog.feed()
            time.sleep(3)
            watchdog.feed()
            time.sleep(3)
        simState.GPRSState = True
        simState.connectionMode = 1
        simState.pingState = True
        simState.bringUpWirelessConnectionState = True
        sim800_uart.simpleHandle(sim800_uart.uart.read())
        watchdog.feed()
    if not simState.local_IP_address:
        local_IP_address = sim800_uart.sim_getLocalIPAddress()
        if _isSIMBringUp:
            _isSIMBringUp = False
            logger.logSIMBringUp(False)
        if local_IP_address:
            watchdog.feed()
            time.sleep(3)
            watchdog.feed()
            simState.local_IP_address = local_IP_address
        else:
            watchdog.feed()
            if sim800_uart.sim_resetIP():
                simState.reset()
            watchdog.feed()
            return False
    watchdog.feed()
    return True

while True:
    if not setupConnection():
        continue
    pioasm_rxuart.usbOutput(
        handle=pioasm_rxuart.handleGPS, during=5, errorDebug=False)
    if pioasm_rxuart.gpsData.year != 0 and (localtime.tm_year < 2022 or (localtime.tm_wday == 0 and localtime.tm_hour == 0 and localtime.tm_min == 0 and localtime.tm_sec == 0)):
        print(pioasm_rxuart.gpsData.year, pioasm_rxuart.gpsData.month, pioasm_rxuart.gpsData.date,
                                             pioasm_rxuart.gpsData.hour, pioasm_rxuart.gpsData.minute, pioasm_rxuart.gpsData.second)
        rtcTime.datetime = time.struct_time((pioasm_rxuart.gpsData.year, pioasm_rxuart.gpsData.month, pioasm_rxuart.gpsData.date,
                                             pioasm_rxuart.gpsData.hour, pioasm_rxuart.gpsData.minute, pioasm_rxuart.gpsData.second, -1, -1, -1))
        rtc.set_time_source(rtcTime)
    # print(pioasm_rxuart.gpsData)
    receiveResult = None
    for client in simState.clients:
        # client.connectState
        watchdog.feed()
        client.sendState = False
        # if pioasm_rxuart.gpsData.active:
        if not client.connectState:
            if sim800_uart.sim_startConnection(client.channel, client.networkType, client.url, client.port):
                logger.log('connect success!\r\n')
                watchdog.feed()
                # time.sleep(5)
                # watchdog.feed()
                # time.sleep(5)
                # watchdog.feed()
                # time.sleep(5)
                # watchdog.feed()
                client.connectState = True
                heartbeatTime = heartbeatTimes
                uploadData(client, initString.encode())
                watchdog.feed()
            else:
                startConnectionTime -= 1
                watchdog.feed()
                if startConnectionTime <= 0:
                    simState.reset()
                    startConnectionTime = startConnectionTimes
                continue
        else:
            receiveWaitingTimes = 3
            while(receiveWaitingTimes > 0):
                receiveWaitingTimes -= 1
                simReceive = sim800_uart.uart.read()
                if simReceive != None:
                    print(simReceive)
                    logger.log("receive:"+simReceive.decode()+"\r\n")
                    receiveResult = sim800_uart.sim_dataReceiving(simReceive)
                    watchdog.feed()
                    if receiveResult:
                        commandState.handleReceive(
                            receiveResult[0], receiveResult[1])
                        break
                    elif simReceive.find((str(client.channel)+', CLOSED\r\n').encode()) != -1:
                        client.sendState = False
                        client.connectState = False
                        time.sleep(4)
                        watchdog.feed()
                        time.sleep(4)
                        watchdog.feed()                        
                    break
                time.sleep(3)
                watchdog.feed()
            if commandState.commondCode == command.CommandCode.CommandGPS:
                uploadGPS(client)
                commandState.reset()
            elif commandState.commondCode == command.CommandCode.CommandGPS_Forever:
                uploadGPS(client)
            elif commandState.commondCode == command.CommandCode.CommandEval:
                try:
                    eval(commandState.eval)
                except Exception as e:
                    print(e)
                    uploadData(client, str(e).encode())
                commandState.reset()
            elif commandState.commondCode == command.CommandCode.CommandEval_Forever:
                try:
                    eval(commandState.eval)
                except Exception as e:
                    print(e)
            elif commandState.commondCode == command.CommandCode.CommandCam:
                ov7670.cam.capture(ov7670.bitmap)
                ov7670.bitmap.dirty()
                bitmapToHexString(ov7670.bitmap, uploadNum, client)
                commandState.reset()
            elif commandState.commondCode == command.CommandCode.CommandMotor:
                motor1.throttle = commandState.motor1
                motor2.throttle = commandState.motor2
                commandState.reset()
            elif commandState.commondCode == command.CommandCode.CommandMotor1:
                motor1.throttle = commandState.motor1
                commandState.reset()
            elif commandState.commondCode == command.CommandCode.CommandMotor2:
                motor2.throttle = commandState.motor2
                commandState.reset()
            elif commandState.commondCode == command.CommandCode.CommandLED:
                ledTimes = commandState.ledTimes
                while ledTimes > 0:
                    ledTimes -= 1
                    watchdog.feed()
                    led.value = 0
                    time.sleep(commandState.ledDuring)
                    led.value = 1
                    time.sleep(commandState.ledDuring)
            elif commandState.commondCode == command.CommandCode.CommandReset:
                commandState.resetAll()
            elif commandState.commondCode == command.CommandCode.CommandReBoot:
                microcontroller.reset()
            elif commandState.commondCode == command.CommandCode.CommandResetBoot:
                logger.resetBootMode()
            elif commandState.commondCode == command.CommandCode.CommandTemporary:
                logger.logTemporary(commandState.temporary)
                commandState.reset()
            elif commandState.commondCode == command.CommandCode.CommandUpdate:
                logger.updateFile(commandState.update)
                commandState.reset()
            elif commandState.commondCode == command.CommandCode.CommandUpload:
                uploadFile(commandState.upload, client)
                commandState.reset()
            elif commandState.commondCode == command.CommandCode.CommandLog:
                uploadFile('/log/' + str(logger.logInfoPage)+'.log', client)
                commandState.reset()
            elif commandState.commondCode == command.CommandCode.CommandOS:
                uploadData(client, ("temperature:"+str(getTemperature())+",voltage:"+str(getVoltage())).encode())
                commandState.reset()
            elif commandState.commondCode == command.CommandCode.CommandOS_Forever:
                uploadData(client, ("temperature:"+str(getTemperature())+",voltage:"+str(getVoltage())).encode())
            elif heartbeatTime > 0:
                heartbeatTime -= 1
            elif heartbeatTime <= 0:
                heartbeatTime = heartbeatTimes
                uploadHeartBeat(client)
    watchdog.feed()
    led.value = 0
    time.sleep(1)
    led.value = 1
    time.sleep(1)
    localtime = time.localtime()
    print(str(localtime.tm_year)+'-' + str(localtime.tm_mon) + '-' + str(localtime.tm_mday) + " " +
          str(localtime.tm_hour)+':' + str(localtime.tm_min) + ':' + str(localtime.tm_sec))
    watchdog.feed()


# sim800_uart.sim_checkIfConnected()
# # sim800_uart.sim_resetIP()
# sim800_uart.sim_enableMultiConnection()
# sim800_uart.sim_ping()
# sim800_uart.sim_bringUpWirelessConnection()
# sim800_uart.sim_getLocalIPAddress()
# sim800_uart.sim_startConnection(sim800_uart.channel, sim800_uart.networkType, sim800_uart.url, sim800_uart.port)
