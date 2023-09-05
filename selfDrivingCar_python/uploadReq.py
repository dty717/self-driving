import socket
from enum import Enum
socketUploadIP = '192.168.137.56'
socketUploadPort = 1000
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect((socketUploadIP, socketUploadPort))
soc.settimeout(2)
buf = bytearray(100)
# soc.recv()
def _e(data):
    return ("clientSoc.send(str("+str(data)+").encode())").encode()

def backward(during, speed=1):
    soc.send(('motor1.throttle ='+str(speed) +
             ';time.sleep('+str(during)+');motor1.throttle = 0').encode())

def forward(during, speed=1):
    backward(during, -speed)

def right(during, speed=1):
    soc.send(('motor2.throttle ='+str(speed) +
             ';time.sleep('+str(during)+');motor2.throttle = 0').encode())

def left(during, speed=1):
    right(during, -speed)

class DirectionOrder(Enum):
    Forward = 0
    Backward = 1
    MoveStop = 2
    Right = 3
    Left = 4
    RotateStop = 5

def convertDirection(direction):
    if direction == 'f' or direction == 'F' or direction == 'forward' or direction == 'Forward':
        direction = DirectionOrder.Forward
    elif direction == 'b' or direction == 'B' or direction == 'backward' or direction == 'Backward':
        direction = DirectionOrder.Backward
    elif direction == 'm' or direction == 'M' or direction == 'movestop' or direction == 'MoveStop' or direction == 'moveStop':
        direction = DirectionOrder.MoveStop
    elif direction == 'r' or direction == 'R' or direction == 'right' or direction == 'Right':
        direction = DirectionOrder.Right
    elif direction == 'l' or direction == 'L' or direction == 'left' or direction == 'Left':
        direction = DirectionOrder.Left
    elif direction == 'r' or direction == 'R' or direction == 'rotatestop' or direction == 'RotateStop' or direction == 'rotateStop':
        direction = DirectionOrder.RotateStop
    if direction in DirectionOrder:
        return direction

def stopDirection(direction: DirectionOrder):
    if direction == DirectionOrder.Forward:
        return DirectionOrder.MoveStop
    elif direction == DirectionOrder.Backward:
        return DirectionOrder.MoveStop
    elif direction == DirectionOrder.MoveStop:
        return DirectionOrder.MoveStop
    elif direction == DirectionOrder.Left:
        return DirectionOrder.RotateStop
    elif direction == DirectionOrder.Right:
        return DirectionOrder.RotateStop
    elif direction == DirectionOrder.RotateStop:
        return DirectionOrder.RotateStop

def reverseDirection(direction: DirectionOrder):
    if direction == DirectionOrder.Forward:
        return DirectionOrder.Backward
    elif direction == DirectionOrder.Backward:
        return DirectionOrder.Forward
    elif direction == DirectionOrder.MoveStop:
        return DirectionOrder.MoveStop
    elif direction == DirectionOrder.Left:
        return DirectionOrder.Right
    elif direction == DirectionOrder.Right:
        return DirectionOrder.Left
    elif direction == DirectionOrder.RotateStop:
        return DirectionOrder.RotateStop

def stringifyDirection(direction: DirectionOrder, speed: float):
    if direction == DirectionOrder.Forward:
        return 'motor1.throttle = '+str(-speed)
    elif direction == DirectionOrder.Backward:
        return 'motor1.throttle = '+str(speed)
    elif direction == DirectionOrder.MoveStop:
        return 'motor1.throttle = 0'
    elif direction == DirectionOrder.Left:
        return 'motor2.throttle = '+str(-speed)
    elif direction == DirectionOrder.Right:
        return 'motor2.throttle = '+str(speed)
    elif direction == DirectionOrder.RotateStop:
        return 'motor2.throttle = 0'

class DirectionList:
    def __init__(self, direction: any = None, during: float = 0, speed: float = 1):
        if direction and during:
            direction = convertDirection(direction)
            self.directionList = [(direction, 0, during, speed)]
        else:
            self.directionList = []
        pass
    #
    def addDirection(self, direction: any, timestamp: float, during: float, speed: float = 1):
        direction = convertDirection(direction)
        self.directionList.append((direction, timestamp, during, speed))
        return self
    #
    def build(self):
        directionDict = {}
        for (direction, timestamp, during, speed) in self.directionList:
            if directionDict.get(timestamp):
                directionDict[timestamp].append((direction, speed))
            else:
                directionDict[timestamp] = [(direction, speed)]
            if directionDict.get(timestamp+during):
                directionDict[timestamp +
                              during].append((stopDirection(direction), speed))
            else:
                directionDict[timestamp +
                              during] = [(stopDirection(direction), speed)]
        directionDictList = sorted(directionDict.items(), key=lambda x: x[0])    
        lastTimeStamp = 0
        directionListStr = ''
        for (timestamp, directions) in directionDictList:
            directionListStr += 'time.sleep('+str(timestamp - lastTimeStamp)+')\n'
            lastTimeStamp = timestamp
            for (direction, speed) in directions:
                directionListStr += stringifyDirection(direction, speed)+"\n"
        return directionListStr
    def reverse(self):
        maxIntervention = 0
        reverseDirectionList = self.directionList.copy()
        reverseDirectionList.reverse()
        for (direction, timestamp, during, speed) in reverseDirectionList:
            if timestamp + during > maxIntervention:
                maxIntervention = timestamp + during
        reverseDirectionDict = {}
        for (direction, timestamp, during, speed) in reverseDirectionList:
            direction = reverseDirection(direction)
            timestamp = maxIntervention - (timestamp + during)
            if reverseDirectionDict.get(timestamp):
                reverseDirectionDict[timestamp].append((direction, speed))
            else:
                reverseDirectionDict[timestamp] = [(direction, speed)]
            if reverseDirectionDict.get(timestamp+during):
                reverseDirectionDict[timestamp +
                              during].append((stopDirection(direction), speed))
            else:
                reverseDirectionDict[timestamp +
                              during] = [(stopDirection(direction), speed)]
        reverseDirectionDictList = sorted(reverseDirectionDict.items(), key=lambda x: x[0])    
        lastTimeStamp = 0
        reverseDirectionListStr = ''
        for (timestamp, directions) in reverseDirectionDictList:
            reverseDirectionListStr += 'time.sleep('+str(timestamp - lastTimeStamp)+')\n'
            lastTimeStamp = timestamp
            for (direction, speed) in directions:
                reverseDirectionListStr += stringifyDirection(direction, speed)+"\n"
        return reverseDirectionListStr


directionList = DirectionList()
directionList.addDirection('f', 0, 2, 0.6)
directionList.addDirection('r', 1, 1, 0.5)
# print(directionList.reverse())
soc.send(directionList.build().encode())
