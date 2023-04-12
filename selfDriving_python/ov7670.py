
import time
from displayio import (
    Bitmap,
    Group,
    TileGrid,
    FourWire,
    release_displays,
    ColorConverter,
    Colorspace,
)
from adafruit_ov7670 import (
    OV7670,
    OV7670_SIZE_DIV1,
    OV7670_SIZE_DIV16,
)
import board
import busio
import digitalio
import sys

# Ensure the camera is shut down, so that it releases the SDA/SCL lines,
# then create the configuration I2C bus

with digitalio.DigitalInOut(board.GP10) as reset:
    reset.switch_to_output(False)
    time.sleep(0.001)

bus = None
cam = None
bitmap = None
try:
    bus = busio.I2C(board.GP9, board.GP8)
    cam = OV7670(
        bus,
        data_pins=[
            board.GP12,
            board.GP13,
            board.GP14,
            board.GP15,
            board.GP16,
            board.GP17,
            board.GP18,
            board.GP19,
        ],  # [16]     [org] etc
        clock=board.GP11,  # [15]     [blk]
        vsync=board.GP7,  # [10]     [brn]
        href=board.GP22,  # [27/o14] [red]
        mclk=board.GP10,  # [16/o15]
        shutdown=None,
        reset=board.GP21,
    )  # [14]
    cam.size = 1
    bitmap = Bitmap(cam.width, cam.height, 65536)
except Exception as e:
    pass
    # error = e.strerror
    # logging = False

# power = digitalio.DigitalInOut(board.GP6)
# power.direction = digitalio.Direction.OUTPUT

# Set up the camera (you must customize this for your board!)


def handleOV7670Data(handleFun):
    if cam:
        # lastTime = time.time()
        cam.capture(bitmap)
        bitmap.dirty()
        handleFun(bitmap)

def r():
    if cam:
        # lastTime = time.time()
        cam.capture(bitmap)
        bitmap.dirty()
        print('a=`')
        for i in range(cam.width*cam.height):
            print(bitmap[i])
        print('`')
        print('mm=`')
    # print(time.time()-lastTime)

# def r():
#     lastTime = time.time()
#     cam.capture(bitmap)
#     bitmap.dirty()
#     bufTem = []
#     for i in range(cam.width*cam.height):
#         sys.stdout.write(bytes([bitmap[i]&0xff,bitmap[i]>>8]))
#     print(time.time()-lastTime)

# def r():
#     lastTime = time.time()
#     cam.capture(bitmap)
#     bitmap.dirty()
#     strTem = ''
#     for i in range(cam.width):
#         for j in range(cam.height):
#             indexBuf = i*cam.height + j
#             strTem+=str(bitmap[indexBuf])+'\n'
#         print(strTem)
#         strTem = ''
#     print(time.time()-lastTime)


def re(reg):
    b = bytearray(1)
    b[0] = reg
    if bus:
        bus.try_lock()
        bus.writeto(33,b)
        bus.readfrom_into(33,b)
        bus.unlock()
    return b[0]

def w(reg, value):
    b = bytearray(2)
    b[0] = reg
    b[1] = value
    if bus:
        bus.try_lock()
        bus.writeto(33,b)
        bus.unlock()
        time.sleep(0.1)

def configOV7670():
    ### Frame Rate Adjustment for 24Mhz input clock
    # #30 fps, PCLK = 24Mhz
    # w(0x11, 0x80)
    # w(0x6b, 0x0a)
    # w(0x2a, 0x00)
    # w(0x2b, 0x00)
    # w(0x92, 0x00)
    # w(0x93, 0x00)
    # w(0x3b, 0x0a)
    # 
    # 15 fps, PCLK = 12Mhz
    w(0x11, 0x00)
    w(0x6b, 0x0a)
    w(0x2a, 0x00)
    w(0x2b, 0x00)
    w(0x92, 0x00)
    w(0x93, 0x00)
    w(0x3b, 0x0a)
    # 
    ### Banding Filter Setting for 24Mhz Input Clock
    # # 30fps for 60Hz light frequency
    # w(0x13, 0xe7)  #banding filter enable
    # w(0x9d, 0x98)  #50Hz banding filter
    # w(0x9e, 0x7f)  #60Hz banding filter
    # w(0xa5, 0x02)  #3 step for 50hz
    # w(0xab, 0x03)  #4 step for 60hz
    # w(0x3b, 0x02)  #Select 60Hz banding filter
    # 
    # 15fps for 60Hz light frequency
    w(0x13, 0xe7)  #banding filter enable
    w(0x9d, 0x4c)  #50Hz banding filter
    w(0x9e, 0x3f)  #60Hz banding filter
    w(0xa5, 0x05)  #6 step for 50hz
    w(0xab, 0x07)  #8 step for 60hz
    w(0x3b, 0x02)  #Select 60Hz banding filter
    # 
    ### Banding Filter Setting for 24Mhz Input Clock
    # # 30fps for 60Hz light frequency
    # w(0x13, 0xe7)  #banding filter enable
    # w(0x9d, 0x98)  #50Hz banding filter
    # w(0x9e, 0x7f)  #60Hz banding filter
    # w(0xa5, 0x02)  #3 step for 50hz
    # w(0xab, 0x03)  #4 step for 60hz
    # w(0x3b, 0x12)  #Automatic Detect banding filter
    # 
    # 15fps for 60Hz light frequency
    w(0x13, 0xe7)  #banding filter enable
    w(0x9d, 0x4c)  #50Hz banding filter
    w(0x9e, 0x3f)  #60Hz banding filter
    w(0xa5, 0x05)  #6 step for 50hz
    w(0xab, 0x07)  #8 step for 60hz
    w(0x3b, 0x12)  #Automatic Detect banding filter
    # 
    # # fps_30_PCLK_24Mhz_light_60Hz = 0xa1
    # fps_3_125 = 3.125
    # fps_3_75 = 3.75
    # fps_14_3 = 14.3
    # fps_15 = 15
    # fps_25 = 25
    # fps_30 = 30
    # 
    # PCLK_12Mhz = 12
    # PCLK_13Mhz = 13
    # PCLK_24Mhz = 24
    # PCLK_26Mhz = 26
    # 
    # light_60Hz = 60
    # 
    # def setCameraConfig(fps,PCLK,light):
    #     return
    # 
    # Light Mode
    # Cloudy
    # w(0x13, 0xe5)  #AWB off
    # w(0x01, 0x58)
    # w(0x02, 0x60)
    # 
    # Sunny
    # w(0x13, 0xe5) #AWB off
    # w(0x01, 0x5a)
    # w(0x02, 0x5c)
    # Auto
    w(0x13, 0xe7)  #AWB on
    # 
    # For 24Mhz/26Mhz Clock Input
    # # 3.75fps night mode for 60Hz light environment
    # w(0x11, 0x03)
    # w(0x3b, 0x0a)