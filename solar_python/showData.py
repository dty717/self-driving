import re
import numpy as np
import matplotlib.pyplot as plt
import statistics
file = open('stdout.log', encoding='utf-8')
flines = file.readlines()

timeList = []
temperature = []
selfVoltage = []
solarVoltage = []
outputVoltage = []
outputCurrent = []
outputPower = []

usingTimeFilter = False
startTime = np.datetime64("2023-06-10 06:32:12.950")
endTime = np.datetime64("2093-05-31 21:50:12.950")


regex = r'(\d+-\d+-\d+T\d+:\d+:[\d.]+Z)\s+temperature:([\d.]+),self voltage:([\d.]+),solar voltage:([\d.]+),output voltage:([\d.]+),output current:([\d.]+)'
for line in flines:
    matches = re.match(regex, line)
    if matches:
        _time = np.datetime64(matches.groups()[0].replace('T', ' ').replace('Z', ''))
        if usingTimeFilter:
            if _time > endTime or _time < startTime:
                continue
        timeList.append(np.datetime64(_time))
        temperature.append(float(matches.groups()[1]))
        selfVoltage.append(float(matches.groups()[2]))
        solarVoltage.append(float(matches.groups()[3]))
        outputVoltage.append(float(matches.groups()[4]))
        outputCurrent.append(float(matches.groups()[5]))
        outputPower.append(
            float(matches.groups()[5])*float(matches.groups()[4]))


# time temperature self voltage,solar voltage,output voltage,output current
fig, ax = plt.subplots()
# ax.plot(timeList, temperature)
# ax.plot(timeList, selfVoltage)
# ax.plot(timeList, solarVoltage)
ax.plot(timeList, outputVoltage)
ax.plot(timeList, outputCurrent)
# ax.plot(timeList, outputPower)
plt.show()

# statistics.mean(outputPower)
