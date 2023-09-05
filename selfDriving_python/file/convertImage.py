from PIL import Image, ImageDraw
import numpy as np
import time
import serial
cdc_serial_name = 'com28'
cdc_data_name = 'com29'

height = 240
width = 320

## read from file
# rawDataFile = open('capture.txt', mode='rb')
# rawData = rawDataFile.read()
cdc_serial = serial.Serial(cdc_serial_name,timeout=0.2)  # open serial port
cdc_data = serial.Serial(cdc_data_name,timeout=0.2)  # open serial port


def generateImage(rawData):
    rawDataArray = np.zeros((height, width,3))
    for i in range(height):
        for j in range(width):
            bitIndex = i * width + j
            pixel = (rawData[bitIndex * 2] << 8) + rawData[bitIndex * 2+1]
            green_value = ((pixel & 0b111) << 3) ^ (pixel >> 13)
            blue_value = (pixel >> 8) & 0b11111
            red_value = (pixel >> 3) & 0b11111
            red = red_value << 3
            green = green_value << 2
            blue = blue_value << 3
            rawDataArray[i][j] = [red,green,blue]
    im = Image.fromarray(np.array(rawDataArray,dtype = np.uint8))
    return im


for _ in range(100):
    cdc_serial.flush()
    cdc_serial.write(b'r()\r\n')
    while True:
        for i in range(5):
            rawData = cdc_data.readall()
            if len(rawData) > 0:
                print(cdc_serial.read_all())
                break
            time.sleep(1)
        if len(rawData) > 0:
            generateImage(rawData).rotate(180).show()
            break
