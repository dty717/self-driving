import microcontroller

# import storage
# storage.remount("/", False)

logging = False
logInfoPage = 0

def initLog():
    global logging
    global logInfoPage
    try:
        logInfo = open('/log/log.info','r')
        logInfoContent = logInfo.read()
        if logInfoContent:
            logInfoPage = (int(logInfoContent) + 1) % 10
        logging = True
        logInfo.close()
        logInfo = open('/log/log.info','w')
        logInfo.write(str(logInfoPage))
        logInfo.flush()
        logInfo.close()
        with open('/log/' + str(logInfoPage)+'.log', 'w') as updateFile:
            updateFile.write('')
            updateFile.flush()
            updateFile.close()
        with open('/tem.txt', 'w') as temFile:
            temFile.write('')
            temFile.flush()
            temFile.close()
    except Exception as e:
        logging = False
        print(e)

def resetBootMode():
    # if not logging:
    #     return False
    try:
        bootFile = open('boot.py','w')
        bootFile.write('#import storage\r\n')
        bootFile.write('#storage.remount("/", False)\r\n')
        bootFile.flush()
        bootFile.close()
        microcontroller.reset()
        return True
    except Exception as e:
        print(e)
    return False

def logSIMBringUp(isBringUp: bool):
    if not logging:
        return False
    try:
        with open('/sim.txt', 'w') as temFile:
            if isBringUp:
                temFile.write('True')
            else:
                temFile.write('False')
            temFile.flush()
            temFile.close()
        return True
    except Exception as e:
        print(e)
    return False

def isSIMBringUp():
    if not logging:
        return False
    try:
        with open('/sim.txt', 'r') as simFile:
            simBringUpText = simFile.read()
            if simBringUpText == 'True':
                return True
        return False
    except Exception as e:
        print(e)
    return False


def log(logContent: str):
    if not logging:
        return False
    try:
        with open('/log/' + str(logInfoPage)+'.log', 'a') as logFile:
            logFile.write(logContent)
            logFile.flush()
            logFile.close()
        return True
    except Exception as e:
        print(e)
    return False

def logTemporary(logContent: str):
    if not logging:
        return False
    try:
        with open('/tem.txt', 'a') as temFile:
            temFile.write(logContent)
            temFile.flush()
            temFile.close()
        return True
    except Exception as e:
        print(e)
    return False

def updateFile(filePath: str):
    if not logging:
        return False
    try:
        with open('/tem.txt', 'r') as temFile:
            temporary = temFile.read()
            newFile = open(filePath, 'w')
            newFile.write(temporary.encode())
            newFile.flush()
            newFile.close()
            temFile.close()
            temFile = open('/tem.txt', 'r')
            temFile.write('')
            temFile.flush()
            temFile.close()
        return True
    except Exception as e:
        print(e)
    return False