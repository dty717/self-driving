"""CircuitPython Essentials UART Serial example"""
import board
import busio
import time

uart = busio.UART(board.GP0, board.GP1, baudrate=9600, stop=1, parity=None)


class Client:
    def __init__(self, channel, url, networkType, port, beatData, handleRec):
        self.channel = channel
        self.url = url
        self.networkType = networkType
        self.port = port
        self.beatData = beatData
        self.connectState = False
        self.sendState = False
        self.handleRec = handleRec


class SIMState:
    def __init__(self, clients):
        self.reset()
        self.clients = clients
    def reset(self):
        self.functionState = True
        self.signalState = 0
        self.GPRSState = False
        self.connectionMode = 0
        self.pingState = False
        self.bringUpWirelessConnectionState = False
        self.local_IP_address = None
        # 
    # def __str__(self):
    #     return "{}-{}-{} {}:{}:{} active:{} {} {},{} {}".format(self.year, self.month, self.date, self.hour, self.minute, self.second, self.active,
    #                                                             self.latitude, self.latitudeFlag, self.longitude, self.longitudeFlag)

lastReceiveBuf = b''

def sim_dataReceiving(receiveBuf):
    global lastReceiveBuf
    # receiveBuf = uart.read()
    if receiveBuf != None:
        lastReceiveBuf = lastReceiveBuf+receiveBuf
        if lastReceiveBuf.find(b'\r\n+RECEIVE,') != -1:
            lastReceiveBufIndex = lastReceiveBuf.find(b'\r\n+RECEIVE,')
            if lastReceiveBufIndex + len(b'\r\n+RECEIVE,') < len(lastReceiveBuf):
                if lastReceiveBuf.find(b':',lastReceiveBufIndex)!= -1:
                    lastReceiveBufLenIndex = lastReceiveBuf.find(b':\r\n', lastReceiveBufIndex)
                    dataLenStr = lastReceiveBuf[lastReceiveBufIndex + len(b'\r\n+RECEIVE,'):lastReceiveBufLenIndex]
                    if dataLenStr.find(b',') != -1:
                        hasError = False
                        try:
                            channel = int(dataLenStr.split(b',')[0])
                            channelRecLen = int(dataLenStr.split(b',')[1])
                        except:
                            hasError = True
                        if not hasError:
                            if len(lastReceiveBuf[lastReceiveBufLenIndex + len(':\r\n'):]) >= channelRecLen:
                                channelRecBuf = lastReceiveBuf[lastReceiveBufLenIndex + len(':\r\n'): lastReceiveBufLenIndex + len(':\r\n')+channelRecLen]
                                lastReceiveBuf = lastReceiveBuf[lastReceiveBufLenIndex + len(':\r\n')+channelRecLen:]
                                return (channel, channelRecBuf)
        # else:
        if len(lastReceiveBuf) > 256:
            lastReceiveBuf = lastReceiveBuf[-256:]
    return False
        # \r\n+RECEIVE,1,4:\r\n1234\r\n'


def simpleHandle(data):
    if data != None:
        print(data)
    return

def sim_ok():
    simpleHandle(uart.read())
    uart.write(b'AT\r\n')
    time.sleep(0.1)
    res = uart.readline()
    if res == b'AT\r\r\n':
        res = uart.readline()
    if res == b'OK\r\n':
        return True
    else:
        return False


def sim_checkIfOpen():
    simpleHandle(uart.read())
    uart.write(b'AT+CFUN?\r\n')
    time.sleep(0.1)
    res = uart.readline()
    if res == b'AT+CFUN?\r\r\n':
        res = uart.readline()
    if res == b'+CFUN: 1\r\n':
        res = uart.readline()
        if res == b'\r\n':
            res = uart.readline()
        if res == b'OK\r\n':
            return "function open"
        else:
            return "function error"
    elif res == b'+CFUN: 0\r\n':
        res = uart.readline()
        if res == b'\r\n':
            res = uart.readline()
        if res == b'OK\r\n':
            return "function close"
        else:
            return "function error"
    else:
        return "function error"


def sim_close():
    simpleHandle(uart.read())
    uart.write(b'AT+CFUN=0\r\n')
    time.sleep(0.1)
    res = uart.readline()
    print(res)
    if res == b'AT+CFUN=0\r\r\n':
        res = uart.readline()
        print(res)
    else:
        return False
    if res == b'OK\r\n':
        return True
    elif res == b'+CPIN: NOT READY\r\n':
        time.sleep(5)
        res = uart.readline()
        print(res)
        if res == b'\r\n':
            res = uart.readline()
        if res == b'OK\r\n':
            return True
        else:
            return False
    else:
        return False


def sim_open():
    simpleHandle(uart.read())
    uart.write(b'AT+CFUN=1\r\n')
    time.sleep(0.1)
    res = uart.readline()
    print(res)
    if res == '\r\n':
        res = uart.readline()
        print(res)
    if res == b'AT+CFUN=1\r\r\n':
        res = uart.readline()
        print(res)
        if res == b'OK\r\n':
            return True
        elif res == b'+CPIN: READY\r\n':
            res = uart.readline()
            print(res)
            if res == b'\r\n':
                res = uart.readline()
                print(res)
            if res == b'OK\r\n':
                time.sleep(7)
                print("sim open:")
                print(uart.read())
                return True
            else:
                return False
    else:
        return False


def sim_checkForSignal():
    simpleHandle(uart.read())
    uart.write(b'AT+CSQ\r\n')
    time.sleep(0.1)
    res = uart.readline()
    if res == b'AT+CSQ\r\r\n':
        res = uart.readline()
    if res.startswith("+CSQ:") and res.endswith('\r\n'):
        signal = res[5:-2].decode().split(',')
        res = uart.readline()
        if len(signal) == 2:
            if res == b'\r\n':
                res = uart.readline()
            if res == b'OK\r\n':
                return (int(signal[0].strip()), int(signal[1].strip()))
        else:
            return (-1, -1)
    else:
        return (-1, -1)


def sim_checkIfConnected():
    simpleHandle(uart.read())
    uart.write(b'AT+CGATT?\r\n')
    time.sleep(0.5)
    res = uart.readline()
    if res == b'AT+CGATT?\r\r\n':
        res = uart.readline()
    if res == b'+CGATT: 1\r\n':
        res = uart.readline()
        if res == b'\r\n':
            res = uart.readline()
        if res == b'OK\r\n':
            return True
    elif res == b'+CGATT: 0\r\n':
        res = uart.readline()
        if res == b'\r\n':
            res = uart.readline()
        if res == b'OK\r\n':
            return False
    elif res == b'ERROR\r\n':
        return False
    return False


def sim_detactFromGPRS():
    simpleHandle(uart.read())
    uart.write(b'AT+CGATT=0\r\n')
    time.sleep(0.1)
    res = uart.readline()
    print(res)
    if res == b'AT+CGATT=0\r\r\n':
        res = uart.readline()
        print(res)
    if res == b'\r\n':
        res = uart.readline()
        print(res)
    if res == b'OK\r\n':
       return True
    elif res == b'ERROR\r\n':
        return False
    return False


def sim_attachToGPRS():
    simpleHandle(uart.read())
    uart.write(b'AT+CGATT=1\r\n')
    time.sleep(3)
    res = uart.readline()
    print(res)
    if res == b'AT+CGATT=1\r\r\n':
        res = uart.readline()
        print(res)
    if res == b'\r\n':
        res = uart.readline()
        print(res)
    if res == b'OK\r\n':
       return True
    elif res == b'ERROR\r\n':
        return False
    return False


def sim_enableMultiConnection():
    simpleHandle(uart.read())
    uart.write(b'AT+CIPMUX=1\r\n')
    time.sleep(0.1)
    res = uart.readline()
    print(res)
    if res == b'AT+CIPMUX=1\r\r\n':
        res = uart.readline()
        print(res)
    if res == b'\r\n':
        res = uart.readline()
        print(res)
    if res == b'OK\r\n':
       return True
    elif res == b'ERROR\r\n':
        return False
    return False


def sim_ping():
    simpleHandle(uart.read())
    uart.write(b'AT+CSTT\r\n')
    time.sleep(0.1)
    res = uart.readline()
    print(res)
    if res == b'AT+CSTT\r\r\n':
        res = uart.readline()
        print(res)
    if res == b'\r\n':
        res = uart.readline()
        print(res)
    if res == b'OK\r\n':
       return True
    elif res == b'ERROR\r\n':
        return False
    return False


def sim_bringUpWirelessConnection():
    simpleHandle(uart.read())
    uart.write(b'AT+CIICR\r\n')
    time.sleep(0.1)
    res = uart.readline()
    print(res)
    if res == b'AT+CIICR\r\r\n':
        time.sleep(5)
        res = uart.readline()
        print(res)
    if res == b'\r\n':
        res = uart.readline()
        print(res)
    if res == b'OK\r\n':
       return True
    elif res == b'ERROR\r\n':
        return False
    return False


def sim_getLocalIPAddress():
    simpleHandle(uart.read())
    uart.write(b'AT+CIFSR\r\n')
    time.sleep(0.1)
    res = uart.readline()
    print(res)
    if res.endswith(b'AT+CIFSR\r\r\n'):
        res = uart.readline()
        print(res)
    ipList = res.strip().split(b'.')
    if len(ipList) == 4:
        return (int(ipList[0]), int(ipList[1]), int(ipList[2]), int(ipList[3]))
    else:
        return None


def sim_resetIP():
    simpleHandle(uart.read())
    uart.write(b'AT+CIPSHUT\r\n')
    time.sleep(3)
    res = uart.readline()
    print(res)
    if res == b'AT+CIPSHUT\r\r\n':
        res = uart.readline()
        print(res)
    if res == b'\r\n':
        res = uart.readline()
        print(res)
    if res == b'SHUT OK\r\n':
       return True
    elif res == b'ERROR\r\n':
        return False
    return False


def sim_startConnection(channel, networkType, url, port):
    simpleHandle(uart.read())
    startConnectionStr = ('AT+CIPSTART='+str(channel)+',"' +
                          networkType+'","'+url+'",'+str(port))
    uart.write((startConnectionStr+'\r\n').encode())
    time.sleep(0.1)
    res = uart.readline()
    print(res)
    if res == (startConnectionStr+'\r\r\n').encode():
        res = uart.readline()
        print(res)
    if res == b'OK\r\n':
        res = uart.readline()
        print(res)
        if res == b'\r\n':
            time.sleep(5.5)
            res = uart.readline()
            print(res)
        if res == (str(channel)+', CONNECT OK\r\n').encode():
            return True
        elif res == (str(channel)+', CONNECT FAIL\r\n').encode():
            return False
        return False
    elif res == b'ERROR\r\n':
        res = uart.readline()
        print(res)
        if res == b'\r\n':
            res = uart.readline()
            print(res)
        if res == (str(channel)+', ALREADY CONNECT\r\n').encode():
            return True
        return False
    return False


def sim_dataSending(channel, dataBuf):
    simpleHandle(uart.read())
    dataSendingStr = 'AT+CIPSEND='+str(channel)+','+str(len(dataBuf))
    uart.write((dataSendingStr+'\r\n').encode())
    time.sleep(0.1)
    res = uart.readline()
    print(res)
    if res == (dataSendingStr+'\r\r\n').encode():
        res = uart.readline()
        time.sleep(0.1)
        print(res)
    if res == b'> ':
        uart.write(dataBuf+b"\r\n")
        return True
    return False

# def sim_dataReceiving(dataBuf):
#     # 
#     return
  
# time.sleep(3+len(dataStr)/300)
        # res = uart.read()
        # print(res)
        # if res.startswith(dataStr.encode()) and res.endwith((str(channel)+', SEND OK\r\n').encode()):
        # return True
        # return False

# channel = 2
# networkType = "udp"
# url = "155.138.195.23"
# port = 41234

# sim_checkIfConnected()
# sim_enableMultiConnection()
# sim_ping()
# sim_bringUpWirelessConnection()
# sim_getLocalIPAddress()
# sim_startConnection(channel, networkType, url, port)
