# SPDX-FileCopyrightText: 2021 Jeff Epler, written for Adafruit Industries
#
# SPDX-License-Identifier: MIT
#
# Adapted from the example https://github.com/raspberrypi/pico-examples/tree/master/pio/hello_pio

import time
import board
import rp2pio
import adafruit_pioasm

time_zone_shift = 8
lat_deg = 30
lon_deg = 100

uart_rx = """
.program uart_rx
; Slightly more fleshed-out 8n1 UART receiver which handles framing errors and
; break conditions more gracefully.
; IN pin 0 and JMP pin are both mapped to the GPIO used as UART RX.
start:
    wait 0 pin 0        ; Stall until start bit is asserted
    set x, 7    [10]    ; Preload bit counter, then delay until halfway through
bitloop:                ; the first data bit (12 cycles incl wait, set).
    in pins, 1          ; Shift data bit into ISR
    jmp x-- bitloop [6] ; Loop 8 times, each loop iteration is 8 cycles
    jmp pin good_stop   ; Check stop bit (should be high)
    irq 4 rel           ; Either a framing error or a break. Set a sticky flag,
    wait 1 pin 0        ; and wait for line to return to idle state.
    jmp start           ; Don't push data if we didn't see good framing.
good_stop:              ; No delay before returning to start; a little slack is
    push                ; important in case the TX clock is slightly too fast.
"""

assembled = adafruit_pioasm.assemble(uart_rx)

sm = rp2pio.StateMachine(
    assembled,
    frequency=9600*8,
    first_in_pin=board.GP20,
    jmp_pin=board.GP20
)

def usbOutput(handle=print, during=10, errorDebug=False):
    now = time.time()
    buf = bytearray(100)
    bufStr = ""
    while True:
        if sm.in_waiting != 0:
            sm.readinto(buf)
            try:
                bufStr += str(bytes(buf).decode())
            except:
                if errorDebug:
                    print("error")
                    print(buf)
                    if time.time() - now > during:
                        return
                continue
            bufStrList = bufStr.split('\r\n')
            for e in bufStrList[0:-1]:
                handle(e)
            bufStr = bufStrList[-1]
        if time.time() - now > during:
            return


class GpsType:
    GPGSV = 0
    GNGLL = 1
    GNRMC = 2
    GNVTG = 3
    GNGGA = 4
    GNGSA = 5
    GPRMC = 6


class GpsData:
    def __init__(self):
        self.year = 0
        self.month = 0
        self.date = 0
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.active = ''
        self.latitude = lat_deg
        self.latitudeFlag = ''
        self.longitude = lon_deg
        self.longitudeFlag = ''
    #
    def __str__(self):
        return "{}-{}-{} {}:{}:{} active:{} {} {},{} {}".format(self.year, self.month, self.date, self.hour, self.minute, self.second, self.active,
                                                                self.latitude, self.latitudeFlag, self.longitude, self.longitudeFlag)


gpsData = GpsData()


def getGpsInfo(gpsString):
    global gpsData
    gpsType = None
    active = gpsData.active
    if gpsString != None and gpsString != "":
        if gpsString.find(b'$GPRMC') == 0:
            gpsType = GpsType.GPRMC
        if gpsType != None:
            pointIndex = 7
            startIndex = 7
            strLen = len(gpsString)
            while pointIndex < strLen:
                pointIndex += 1
                if gpsString[pointIndex-1] == b','[0]:
                    if pointIndex > startIndex+5:
                        try:
                            gpsData.hour = (int(
                                gpsString[startIndex:startIndex+2]) + time_zone_shift) % 24
                            gpsData.minute = int(
                                gpsString[startIndex+2:startIndex+4])
                            gpsData.second = int(
                                gpsString[startIndex+4:startIndex+6])
                        except:
                            return
                    startIndex = pointIndex
                    break
            while pointIndex < strLen:
                pointIndex += 1
                if gpsString[pointIndex-1] == b','[0]:
                    if pointIndex > startIndex + 1:
                        active = gpsString[startIndex] == b'A'[0]
                    startIndex = pointIndex
                    break
            while pointIndex < strLen:
                pointIndex += 1
                if gpsString[pointIndex-1] == b','[0]:
                    if pointIndex > startIndex + 1:
                        try:
                            gpsData.latitude = float(
                                gpsString[startIndex:pointIndex-1])
                            gpsData.latitude = int(
                                gpsData.latitude/100) + (gpsData.latitude % 100)/60
                        except:
                            return
                    startIndex = pointIndex
                    break
            while pointIndex < strLen:
                pointIndex += 1
                if gpsString[pointIndex-1] == b','[0]:
                    if pointIndex > startIndex + 1:
                        gpsData.latitudeFlag = chr(gpsString[startIndex])
                    startIndex = pointIndex
                    break
            while pointIndex < strLen:
                pointIndex += 1
                if gpsString[pointIndex-1] == b','[0]:
                    if pointIndex > startIndex + 1:
                        try:
                            gpsData.longitude = float(
                                gpsString[startIndex:pointIndex-1])
                            gpsData.longitude = int(
                                gpsData.longitude/100) + (gpsData.longitude % 100)/60
                        except:
                            return
                    startIndex = pointIndex
                    break
            while pointIndex < strLen:
                pointIndex += 1
                if gpsString[pointIndex-1] == b','[0]:
                    if pointIndex > startIndex + 1:
                        gpsData.longitudeFlag = chr(gpsString[startIndex])
                    startIndex = pointIndex
                    break
            while pointIndex < strLen:
                pointIndex += 1
                if gpsString[pointIndex-1] == b','[0]:
                    if pointIndex > startIndex + 1:
                        pass
                    startIndex = pointIndex
                    break
            while pointIndex < strLen:
                pointIndex += 1
                if gpsString[pointIndex-1] == b','[0]:
                    if pointIndex > startIndex + 1:
                        pass
                    startIndex = pointIndex
                    break
            while pointIndex < strLen:
                pointIndex += 1
                if gpsString[pointIndex-1] == b','[0]:
                    if pointIndex > startIndex + 5:
                        try:
                            gpsData.date = int(
                                gpsString[startIndex:startIndex+2])
                            gpsData.month = int(
                                gpsString[startIndex+2:startIndex+4])
                            gpsData.year = int(
                                gpsString[startIndex+4:startIndex+6]) + 2000
                        except:
                            return
                    startIndex = pointIndex
                    break
        gpsData.active = active

def handleGPS(gpsString):
    global gpsData
    getGpsInfo(gpsString.encode())

def resetGPSActive():
    global gpsData
    gpsData.active = False
