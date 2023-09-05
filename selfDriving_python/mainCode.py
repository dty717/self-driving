from ov7670 import configOV7670, cam, bitmap
from digitalio import DigitalInOut, Direction
from time import sleep, localtime as getLocaltime, struct_time
from rtc import set_time_source
from board import LED,GP2,GP3,GP4,GP5
from microcontroller import reset
from sim800_uart import Client,SIMState,sim_dataSending,uart,sim_dataReceiving,sim_startConnection,sim_checkGPRSContext,\
    sim_setNTPUseBearProfile1,sim_setNTPServer,sim_openGPRSContext,sim_startSynchronizeNTP,sim_checkSynchronizeNTP,sim_checkIfOpen,\
    sim_open,sim_checkIfConnected,sim_enableMultiConnection,sim_resetIP,sim_ping,simpleHandle,sim_getLocalIPAddress,sim_close,sim_getLocalTime
from pioasm_rxuart import gpsData,usbOutput,handleGPS
from gc import collect

from command import Command,CommandCode
from pwmio import PWMOut
from adafruit_motor import motor
from logger import initLog,logging,isSIMBringUp,log,logSIMBringUp,rtcTime,resetBootMode,logTemporary,updateFile,logInfoPage
from config import initString, url, networkType, channel, port, lowPowerProtectionVoltage, lowPowerWakeUpVoltage, ntpServer, timeZone, IfUsingNTP, usingWatchDog
from measure import getSelfVoltage, getMeasurement

if usingWatchDog:
    from microcontroller import watchdog
    from watchdog import WatchDogMode

led = DigitalInOut(LED)
led.direction = Direction.OUTPUT
if usingWatchDog:
    watchdog.timeout = 8
    watchdog.mode = WatchDogMode.RESET

index = 5
while index > 0:
    index -= 1
    led.value = led.value ^ 0b1
    sleep(1)

led.value = 0
if usingWatchDog:
    watchdog.feed()

initLog()

print("logging:"+str(logging))

_isSIMBringUp = isSIMBringUp()

clientSIM = Client(channel, url, networkType, port, "", print)
simState = SIMState([clientSIM])
commandState = Command()


PIN_MOTOR1_A = GP2  # pick any pwm pins on their own channels
PIN_MOTOR1_B = GP3
# DC motor setup
# DC Motors generate electrical noise when running that can reset the microcontroller in extreme
# cases. A capacitor can be used to help prevent this.
pwm_motor1_a = PWMOut(PIN_MOTOR1_A, frequency=50)
pwm_motor1_b = PWMOut(PIN_MOTOR1_B, frequency=50)
motor1 = motor.DCMotor(pwm_motor1_a, pwm_motor1_b)

PIN_MOTOR2_A = GP4  # pick any pwm pins on their own channels
PIN_MOTOR2_B = GP5
# DC motor setup
# DC Motors generate electrical noise when running that can reset the microcontroller in extreme
# cases. A capacitor can be used to help prevent this.
pwm_motor2_a = PWMOut(PIN_MOTOR2_A, frequency=50)
pwm_motor2_b = PWMOut(PIN_MOTOR2_B, frequency=50)
motor2 = motor.DCMotor(pwm_motor2_a, pwm_motor2_b)

configOV7670()

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
    simRecBuf = bytearray(500)
    if sim_dataSending(client.channel, data):
        while sendTimes > 0:
            sendTimes -= 1
            bufLen = uart.readinto(simRecBuf)
            simReceive = bytes(simRecBuf[0:bufLen])
            print(simReceive)
            if usingWatchDog:
                watchdog.feed()
            if bufLen != 0:
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
                    receiveResult = sim_dataReceiving(simReceive)
                    if receiveResult:
                        commandState.handleReceive(
                            receiveResult[0], receiveResult[1])
                        return False
                elif len(simRes) > 128:
                    simRes = simRes[-128:]
            if usingWatchDog:
                watchdog.feed()
    else:
        if usingWatchDog:
            watchdog.feed()
        sleep(4)
        if usingWatchDog:
            watchdog.feed()
        for i in range(3):
            if sim_startConnection(client.channel, client.networkType, client.url, client.port):
                if usingWatchDog:
                    watchdog.feed()
                sleep(4)
                if usingWatchDog:
                    watchdog.feed()
                return uploadData(client, data, sendTimes)
            if usingWatchDog:
                watchdog.feed()
        client.connectState = False
        return False


def bitmapToHexString(bitmap, length, client):
    bitmapLen = bitmap.width * bitmap.height
    frameIndex = 0
    if usingWatchDog:
        watchdog.feed()
    uploadData(client,  ("img:"+str(bitmapLen)+"," +
               str(length)).encode(), sendTimes=7000)
    for index in range(0, bitmapLen, length):
        frameIndex += 1
        if usingWatchDog:
            watchdog.feed()
        if index+length >= bitmapLen:
            temBuf = bytearray((bitmapLen-index)*2+len("#" + str(frameIndex) + ":"))
            temBuf[0:len("#" + str(frameIndex) + ":")] = ("#" + str(frameIndex) + ":").encode()
            for i in range(index, bitmapLen):
                # temBuf += bytes([bitmap[i] >> 8, bitmap[i] & 0xff])
                temBuf[2*i] = bitmap[i] >> 8
                temBuf[2*i+1] = bitmap[i] & 0xff
            if not uploadData(client,  ("#" + str(frameIndex) +
                                        ":").encode()+temBuf, sendTimes=7000):
                return
        else:
            temBuf = bytearray(length*2+len("#" + str(frameIndex) + ":"))
            temBuf[0:len("#" + str(frameIndex) + ":")] = ("#" + str(frameIndex) + ":").encode()
            for i in range(index, length+index):
                # temBuf += bytes([bitmap[i] >> 8, bitmap[i] & 0xff])
                temBuf[2*i] = bitmap[i] >> 8
                temBuf[2*i+1] = bitmap[i] & 0xff
            if not uploadData(client, temBuf, sendTimes=7000):
                return
    return


def uploadFile(filePath, client):
    buf = bytearray(500)
    try:
        file = open(filePath, 'r')
    except Exception as e:
        uploadData(client, str(e).encode(), sendTimes=7000)
        log(str(e))
        return False
    fileReadLen = file.readinto(buf)
    if fileReadLen == 0:
        uploadData(client, b'[empty file]', sendTimes=7000)
        file.close()
        return True
    while True:
        if usingWatchDog:
            watchdog.feed()
        if fileReadLen == 0:
            return True
        elif fileReadLen < 500:
            uploadData(client,  buf[0:fileReadLen], sendTimes=7000)
        else:
            uploadData(client,  buf, sendTimes=7000)
        fileReadLen = file.readinto(buf)


def uploadGPS(client):
    return uploadData(client, str(gpsData).encode())


def uploadHeartBeat(client):
    return uploadData(client, b'.')


def setUploadNum(num: int):
    global uploadNum
    uploadNum = num


bringUpWirelessConnectionTimes = 10
bringUpWirelessConnectionTime = bringUpWirelessConnectionTimes
bringUpWirelessConnectionState = False
localtime = getLocaltime()
# rtcTime = rtc.RTC()
closeSearchIndex = 0
hasLowerTurnOff = False


def synchronizeNTP():
    if not sim_checkGPRSContext():
        if usingWatchDog:
            watchdog.feed()
        if not sim_openGPRSContext():
            if usingWatchDog:
                watchdog.feed()
            return False
    if usingWatchDog:
        watchdog.feed()
    if not sim_setNTPUseBearProfile1():
        if usingWatchDog:
            watchdog.feed()
        return False
    if usingWatchDog:
        watchdog.feed()
    if not sim_setNTPServer(ntpServer, timeZone):
        if usingWatchDog:
            watchdog.feed()
        return False
    if usingWatchDog:
        watchdog.feed()
    if not sim_startSynchronizeNTP():
        if usingWatchDog:
            watchdog.feed()
        return False
    if usingWatchDog:
        watchdog.feed()
    for i in range(3):
        sleep(3)
        if usingWatchDog:
            watchdog.feed()
        if sim_checkSynchronizeNTP():
            if usingWatchDog:
                watchdog.feed()
            return True
        if usingWatchDog:
            watchdog.feed()
    return False


def setupConnection():
    global _isSIMBringUp, simState, bringUpWirelessConnectionTime, bringUpWirelessConnectionTime, bringUpWirelessConnectionState
    sleep(1)
    if not _isSIMBringUp:
        if not simState.GPRSState:
            if sim_checkIfOpen():
                if usingWatchDog:
                    watchdog.feed()
            else:
                sim_open()
                if usingWatchDog:
                    watchdog.feed()
                return False
            if sim_checkIfConnected():
                if usingWatchDog:
                    watchdog.feed()
                simState.GPRSState = True
            else:
                if usingWatchDog:
                    watchdog.feed()
                return False
        if not simState.connectionMode:
            if sim_enableMultiConnection():
                if usingWatchDog:
                    watchdog.feed()
                simState.connectionMode = 1
            else:
                if usingWatchDog:
                    watchdog.feed()
                if sim_resetIP():
                    simState.reset()
                if usingWatchDog:
                    watchdog.feed()
                return False
        if not simState.pingState:
            if sim_ping():
                if usingWatchDog:
                    watchdog.feed()
                sleep(3)
                if usingWatchDog:
                    watchdog.feed()
                simState.pingState = True
            else:
                if usingWatchDog:
                    watchdog.feed()
                if sim_resetIP():
                    simState.reset()
                if usingWatchDog:
                    watchdog.feed()
                return False
        if not simState.bringUpWirelessConnectionState:
            bringUpWirelessConnectionTime = bringUpWirelessConnectionTimes
            simpleHandle(uart.read())
            logSIMBringUp(True)
            uart.write(b'AT+CIICR\r\n')
            sleep(0.1)
            logSIMBringUp(False)
            res = uart.readline()
            print(res)
            if res == b'AT+CIICR\r\r\n':
                sleep(5)
                # print(res)
            bringUpWirelessConnectionState = False
            while bringUpWirelessConnectionTime > 0:
                if usingWatchDog:
                    watchdog.feed()
                sleep(3)
                if usingWatchDog:
                    watchdog.feed()
                res = uart.readline()
                print(res)
                bringUpWirelessConnectionTime -= 1
                if res == b'\r\n':
                    res = uart.readline()
                    print(res)
                if res == b'OK\r\n':
                    bringUpWirelessConnectionState = True
                    break
                elif res == b'ERROR\r\n':
                    bringUpWirelessConnectionState = False
                    break
            if bringUpWirelessConnectionState:
                if usingWatchDog:
                    watchdog.feed()
                sleep(3)
                if usingWatchDog:
                    watchdog.feed()
                simState.bringUpWirelessConnectionState = True
            else:
                if usingWatchDog:
                    watchdog.feed()
                sleep(3)
                if usingWatchDog:
                    watchdog.feed()
                if sim_resetIP():
                    simState.reset()
                if usingWatchDog:
                    watchdog.feed()
                sleep(3)
                if usingWatchDog:
                    watchdog.feed()
                return False
    else:
        print("waiting for wireless connection bring up")
        for i in range(5):
            if usingWatchDog:
                watchdog.feed()
            sleep(3)
            if usingWatchDog:
                watchdog.feed()
            sleep(3)
        simState.GPRSState = True
        simState.connectionMode = 1
        simState.pingState = True
        simState.bringUpWirelessConnectionState = True
        simpleHandle(uart.read())
        if usingWatchDog:
            watchdog.feed()
    if not simState.local_IP_address:
        local_IP_address = sim_getLocalIPAddress()
        if _isSIMBringUp:
            _isSIMBringUp = False
            logSIMBringUp(False)
        if local_IP_address:
            if usingWatchDog:
                watchdog.feed()
            sleep(3)
            if usingWatchDog:
                watchdog.feed()
            simState.local_IP_address = local_IP_address
        else:
            if usingWatchDog:
                watchdog.feed()
            if sim_resetIP():
                simState.reset()
            if usingWatchDog:
                watchdog.feed()
            return False
    if usingWatchDog:
        watchdog.feed()
    return True


print('power voltage:'+str(getSelfVoltage())+"V")

while True:
    collect()
    if getSelfVoltage() < lowPowerProtectionVoltage:
        if not hasLowerTurnOff:
            hasLowerTurnOff = True
            sim_close()
            simState.reset()
            print('low power voltage:'+str(getSelfVoltage())+"V")
            led.value = 0
            log('low power protect\r\n')
        if usingWatchDog:
            watchdog.feed()
        sleep(3)
        if usingWatchDog:
            watchdog.feed()
        continue
    else:
        if hasLowerTurnOff:
            if getSelfVoltage() > lowPowerWakeUpVoltage:
                hasLowerTurnOff = False
                sim_open()
                if usingWatchDog:
                    watchdog.feed()
                sleep(3)
                if usingWatchDog:
                    watchdog.feed()
                led.value = 1
                log('low power wake up\r\n')
            continue
    if not setupConnection():
        continue
    usbOutput(
        handle=handleGPS, during=5, errorDebug=False)
    if rtcTime.datetime.tm_year <= 2020:
        if gpsData.year != 0 and (localtime.tm_year < 2022 or (localtime.tm_wday == 0 and localtime.tm_hour == 0 and localtime.tm_min == 0 and localtime.tm_sec == 0)):
            print(gpsData.year, gpsData.month, gpsData.date,
                  gpsData.hour, gpsData.minute, gpsData.second)
            rtcTime.datetime = struct_time((gpsData.year, gpsData.month, gpsData.date,
                                                   gpsData.hour, gpsData.minute, gpsData.second, -1, -1, -1))
            set_time_source(rtcTime)
        else:
            if IfUsingNTP and synchronizeNTP():
                sim800_localtime = sim_getLocalTime()
                if sim800_localtime:
                    rtcTime.datetime = sim800_localtime
                    set_time_source(rtcTime)
    receiveResult = None
    for client in simState.clients:
        if usingWatchDog:
            watchdog.feed()
        client.sendState = False
        if not client.connectState:
            if sim_startConnection(client.channel, client.networkType, client.url, client.port):
                log('connect success!\r\n')
                if usingWatchDog:
                    watchdog.feed()
                client.connectState = True
                heartbeatTime = heartbeatTimes
                uploadData(client, initString.encode())
                if usingWatchDog:
                    watchdog.feed()
            else:
                startConnectionTime -= 1
                if usingWatchDog:
                    watchdog.feed()
                if startConnectionTime <= 0:
                    simState.reset()
                    startConnectionTime = startConnectionTimes
                continue
        else:
            receiveWaitingTimes = 3
            while(receiveWaitingTimes > 0):
                receiveWaitingTimes -= 1
                simReceive = uart.read()
                if simReceive != None:
                    print(simReceive)
                    log("receive:"+simReceive.decode()+"\r\n")
                    receiveResult = sim_dataReceiving(simReceive)
                    if usingWatchDog:
                        watchdog.feed()
                    if receiveResult:
                        commandState.handleReceive(
                            receiveResult[0], receiveResult[1])
                        break
                    elif simReceive.find((str(client.channel)+', CLOSED\r\n').encode()) != -1:
                        client.sendState = False
                        client.connectState = False
                        sleep(4)
                        if usingWatchDog:
                            watchdog.feed()
                        sleep(4)
                        if usingWatchDog:
                            watchdog.feed()
                    break
                sleep(3)
                if usingWatchDog:
                    watchdog.feed()
            if commandState.commondCode == CommandCode.CommandGPS:
                uploadGPS(client)
                commandState.reset()
            elif commandState.commondCode == CommandCode.CommandGPS_Forever:
                uploadGPS(client)
            elif commandState.commondCode == CommandCode.CommandEval:
                try:
                    eval(commandState.eval)
                except Exception as e:
                    print(e)
                    uploadData(client, str(e).encode())
                commandState.reset()
            elif commandState.commondCode == CommandCode.CommandEval_Forever:
                try:
                    eval(commandState.eval)
                except Exception as e:
                    print(e)
            elif commandState.commondCode == CommandCode.CommandCam:
                cam.capture(bitmap)
                bitmap.dirty()
                bitmapToHexString(bitmap, uploadNum, client)
                commandState.reset()
            elif commandState.commondCode == CommandCode.CommandMotor:
                motor1.throttle = commandState.motor1
                motor2.throttle = commandState.motor2
                commandState.reset()
            elif commandState.commondCode == CommandCode.CommandMotor1:
                motor1.throttle = commandState.motor1
                commandState.reset()
            elif commandState.commondCode == CommandCode.CommandMotor2:
                motor2.throttle = commandState.motor2
                commandState.reset()
            elif commandState.commondCode == CommandCode.CommandLED:
                ledTimes = commandState.ledTimes
                while ledTimes > 0:
                    ledTimes -= 1
                    if usingWatchDog:
                        watchdog.feed()
                    led.value = 0
                    sleep(commandState.ledDuring)
                    led.value = 1
                    sleep(commandState.ledDuring)
            elif commandState.commondCode == CommandCode.CommandReset:
                commandState.resetAll()
            elif commandState.commondCode == CommandCode.CommandReBoot:
                reset()
            elif commandState.commondCode == CommandCode.CommandResetBoot:
                resetBootMode()
            elif commandState.commondCode == CommandCode.CommandTemporary:
                logTemporary(commandState.temporary)
                commandState.reset()
            elif commandState.commondCode == CommandCode.CommandUpdate:
                updateFile(commandState.update)
                commandState.reset()
            elif commandState.commondCode == CommandCode.CommandUpload:
                uploadFile(commandState.upload, client)
                commandState.reset()
            elif commandState.commondCode == CommandCode.CommandLog:
                uploadFile('/log/' + str(logInfoPage)+'.log', client)
                commandState.reset()
            elif commandState.commondCode == CommandCode.CommandOS:
                uploadData(client, getMeasurement().encode())
                commandState.reset()
            elif commandState.commondCode == CommandCode.CommandOS_Forever:
                uploadData(client, getMeasurement().encode())
            elif heartbeatTime > 0:
                heartbeatTime -= 1
            elif heartbeatTime <= 0:
                heartbeatTime = heartbeatTimes
                uploadHeartBeat(client)
    if usingWatchDog:
        watchdog.feed()
    led.value = 0
    sleep(1)
    led.value = 1
    sleep(1)
    localtime = getLocaltime()
    print(str(localtime.tm_year)+'-' + str(localtime.tm_mon) + '-' + str(localtime.tm_mday) + " " +
          str(localtime.tm_hour)+':' + str(localtime.tm_min) + ':' + str(localtime.tm_sec))
    if usingWatchDog:
        watchdog.feed()
