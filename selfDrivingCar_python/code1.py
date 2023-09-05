
import digitalio
import time
import board
import pwmio
from adafruit_motor import motor

import wifi
import socketpool

import time
import board
import microcontroller
import digitalio

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


def getTemperature():
    return microcontroller.cpu.temperature

# wifi.radio.connect(ssid = "DESKTOP-18", password =  "12345678")
# wifi.radio.connect(ssid = "@PHICOMM_FC_502", password =  "52180362")
# wifi.radio.connect(ssid = "ChinaNet-hvQL", password =  "pwuxkuvg")

socket = socketpool.SocketPool(wifi.radio)

sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

# sock.bind(["0.0.0.0",1000])
# buf = bytearray(100)
# while True:
#     recLen, address = sock.recvfrom_into(buf)
#     try:
#         recData = bytes(buf[0:recLen]).decode()
#         print(recData)
#         evalValue = eval(recData)
#         sock.sendto(str(evalValue).encode(), address)
#     except Exception as err:
#         print(err)
#         sock.sendto(str(err).encode(), address)


sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
sock.bind(("0.0.0.0",1000))
sock.listen(1000)
recLenMax = 128
buf = bytearray(recLenMax)
while True:
    clientSoc,clientAddr = sock.accept()
    while True:
        recLen = clientSoc.recv_into(buf)
        recData = bytes(buf[0:recLen])
        if recLen == recLenMax:
            clientSoc.settimeout(0.1)
            while True:
                try:
                    recLen = clientSoc.recv_into(buf)
                    recData += bytes(buf[0:recLen])
                    if recLen !=recLenMax:
                        break
                except Exception as err:
                    break
            clientSoc.settimeout(None)
        if recLen == 0:
            break
        try:
            print(recData)
            lastReceive =  recData.split(b'\n')
            exec(recData)
            # if evalValue!=None:
            # clientSoc.send(str(evalValue).encode())
        except Exception as err:
            print(err)
            clientSoc.send(str(err).encode())
            time.sleep(5)
            clientSoc.send(recData)


# motor1.throttle = 1
# motor1.throttle = 1
# while True:
#     time.sleep(1)
#     motor1.throttle = 0.5
#     time.sleep(1)
#     motor1.throttle = -0.5
#     time.sleep(1)
#     motor2.throttle = 1
#     time.sleep(1)
#     motor2.throttle = -1
