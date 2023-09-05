
initString = "ABC:1000001"
channel = 2
networkType = "udp"
url = "155.138.195.23"
port = 41234
lowPowerProtectionVoltage = 3.62
lowPowerWakeUpVoltage = 3.68
ntpServer = "pool.ntp.org"
timeZone = 32

class CommandCode:
    CommandIdle = 0
    CommandGPS = 1
    CommandGPS_Forever = 2
    CommandEval = 3
    CommandEval_Forever = 4
    CommandCam = 5
    CommandMotor = 6
    CommandMotor1 = 7
    CommandMotor2 = 8
    CommandLED = 9
    CommandReset = 10
    CommandReBoot = 11
    CommandResetBoot = 12
    CommandTemporary = 13
    CommandUpdate = 14
    CommandUpload = 15
    CommandLog = 16
    CommandOS = 17
    CommandOS_Forever = 18

commondCodeInit = CommandCode.CommandGPS_Forever
