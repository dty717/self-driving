from config import CommandCode, commondCodeInit

class Command:
    def __init__(self):
        self.resetAll()
        self.commondCode = commondCodeInit
    def handleReceive(self, channel, channelRecBuf):
        self.commondStr = channelRecBuf
        if channelRecBuf.find(b'[|gps|]') != -1:
            self.commondCode = CommandCode.CommandGPS
        elif channelRecBuf.find(b'[|gps forever|]') != -1:
            self.commondCode = CommandCode.CommandGPS_Forever
        elif channelRecBuf.find(b'[|eval|]:') != -1:
            self.commondCode = CommandCode.CommandEval
            self.eval = channelRecBuf[channelRecBuf.find(b'[|eval|]:') + len(b'[|eval|]:'):]
        elif channelRecBuf.find(b'[|eval forever|]:') != -1:
            self.commondCode = CommandCode.CommandEval_Forever
            self.eval = channelRecBuf[channelRecBuf.find(b'[|eval|]:') + len(b'[|eval|]:'):]
        elif channelRecBuf.find(b'[|cam|]') != -1:
            self.commondCode = CommandCode.CommandCam
        elif channelRecBuf.find(b'[|motor|]:') != -1:
            self.commondCode = CommandCode.CommandMotor
            try:
                self.motor1 = float(channelRecBuf[channelRecBuf.find(b'[|motor|]:') + len(b'[|motor|]:'):])
                self.motor2 = self.motor1
            except Exception as e:
                print(e)
        elif channelRecBuf.find(b'[|motor1|]:') != -1:
            self.commondCode = CommandCode.CommandMotor1
            try:
                self.motor1 = float(channelRecBuf[channelRecBuf.find(b'[|motor1|]:') + len(b'[|motor1|]:'):])
            except Exception as e:
                print(e)
        elif channelRecBuf.find(b'[|motor2|]:') != -1:
            self.commondCode = CommandCode.CommandMotor2
            try:
                self.motor2 = float(channelRecBuf[channelRecBuf.find(b'[|motor2|]:') + len(b'[|motor2|]:'):])
            except Exception as e:
                print(e)
        elif channelRecBuf.find(b'[|led|]:') != -1:
            self.commondCode = CommandCode.CommandLED
            try:
                ledStr = channelRecBuf[channelRecBuf.find(b'[|led|]:') + len(b'[|led|]:'):].decode()
                self.ledDuring = float(ledStr.split(',')[0])
                self.ledTimes = int(ledStr.split(',')[1])
            except Exception as e:
                print(e)
        elif channelRecBuf.find(b'[|reset|]') != -1:
            self.commondCode = CommandCode.CommandReset
        elif channelRecBuf.find(b'[|reboot|]') != -1:
            self.commondCode = CommandCode.CommandReBoot
        elif channelRecBuf.find(b'[|reset boot|]') != -1:
            self.commondCode = CommandCode.CommandResetBoot
        elif channelRecBuf.find(b'[|tem|]:') != -1:
            self.commondCode = CommandCode.CommandTemporary
            self.temporary = channelRecBuf[channelRecBuf.find(b'[|tem|]:') + len(b'[|tem|]:'):]
        elif channelRecBuf.find(b'[|update|]:') != -1:
            self.commondCode = CommandCode.CommandUpdate
            self.update = channelRecBuf[channelRecBuf.find(b'[|update|]:') + len(b'[|update|]:'):]
        elif channelRecBuf.find(b'[|upload|]:') != -1:
            self.commondCode = CommandCode.CommandUpload
            self.upload = channelRecBuf[channelRecBuf.find(b'[|upload|]:') + len(b'[|upload|]:'):]
        elif channelRecBuf.find(b'[|log|]') != -1:
            self.commondCode = CommandCode.CommandLog
        elif channelRecBuf.find(b'[|os|]') != -1:
            self.commondCode = CommandCode.CommandOS
        elif channelRecBuf.find(b'[|os forever|]') != -1:
            self.commondCode = CommandCode.CommandOS_Forever
        return
    def reset(self):
        self.commondCode = CommandCode.CommandIdle
    def resetAll(self):
        self.reset()
        self.commondStr = ""
        self.eval = ""
        self.update = ""
        self.upload = ""
        self.temporary = ""
        self.motor1 = 0
        self.motor2 = 0
        self.ledDuring = 0
        self.ledTimes = 0

