import math
import serial
import time

def degToVisca(deg):
    x = math.floor(deg * 14.4)
    if deg < 0:
        return 0xFFFF + x
    else:
        return x

SET = 0x01
GET = 0x09
VALUE = 0x04
PTZ = 0x06
MOVEMENT = 0x01
ABSOLUTE_MOVEMENT = 0x02
RELATIVE_MOVEMENT = 0x03
PTZ_HOME = 0x04
PTZ_RESET = 0x05

class Camera:
    def __init__(self):
        self.conn = serial.Serial()
        self.panSpeed = 16
        self.tiltSpeed = 16
        self.address = 1
        self.flipped = False

    def connect(self, port):
        self.conn.baudrate = 9600
        self.conn.port = port
        self.conn.timeout = 1
        self.conn.open()
        self.flipped = False

    def connected(self):
        return self.conn.isOpen()

    def commandRead(self, bytes):
        cmd = bytearray([0x80 + self.address])
        cmd.extend(bytes)
        cmd.append(0xFF)
        self.conn.flushInput()
        self.conn.write(cmd)
        return self.conn.read_until(b'\xFF')
    def command(self, bytes):
        cmd = bytearray([0x80 + self.address])
        cmd.extend(bytes)
        cmd.append(0xFF)
        self.conn.flushInput()
        self.conn.write(cmd)
        return

    def setPanSpeed(self, newSpeed):
        assert(newSpeed >= 0 and newSpeed <= 24)
        self.panSpeed = newSpeed
    def setTileSpeed(self, newSpeed):
        assert(newSpeed >= 0 and newSpeed <= 18)
        self.tiltSpeed = newSpeed

    def home(self):
        self.command(bytearray([SET, PTZ, PTZ_HOME]))

    def absoluteMove(self, pan, tilt):
        # 01 06 02 PS TS 0P 0P 0P 0P 0T 0T 0T 0T
        # PS panSpeed, visca speed table
        # TS tiltSpeed, visca speed table 
        # 0P x4, nibblets of the pan position, deg * 14.4
        # 0T x4, nibblets of the tilt position, deg * 14.4
        assert(pan >= -170 and pan <= 170)
        assert(tilt >= -30 and pan <= 90)
        vPan = degToVisca(pan)
        vTilt = degToVisca(tilt)
        cmd = bytearray([
        SET,
        PTZ,
        ABSOLUTE_MOVEMENT,
        self.panSpeed,
        self.tiltSpeed,
        vPan >> 12 & 0x0F, vPan >> 8 & 0x0F, vPan >> 4 & 0x0F, vPan & 0x0F, #pan
        vTilt >> 12 & 0x0F, vTilt >> 8 & 0x0F, vTilt >> 4 & 0x0F, vTilt & 0x0F #tilt
        ])
        self.command(cmd)

    def move(self, pan, tilt):
        #if self.flipped:
        #    pan -= pan * 2
        #    tilt -= tilt *2
        assert(pan >= -1 and pan <= 1)
        assert(tilt >= -1 and tilt <= 1)
        if pan == -1:
            panmod = 0x01
        elif pan == 1:
            panmod = 0x02
        else:
            panmod = 0x03

        if tilt == -1:
            tiltmod = 0x02
        elif tilt == 1:
            tiltmod = 0x01
        else: 
            tiltmod = 0x03

        cmd = bytearray([
            SET,
            PTZ, 
            MOVEMENT,
            self.panSpeed,
            self.tiltSpeed,
            panmod,
            tiltmod
        ])
        self.command(cmd)


    def stop(self):
        self.command(bytearray([SET, PTZ, MOVEMENT, self.panSpeed, self.tiltSpeed, 0x03, 0x03]))

    #set vertical image flipping
    def setVFlip(self, flip):
        self.command(bytearray([
            SET,
            VALUE,
            0x66, #picture flip
            0x02 if flip else 0x03
        ]))

    #set horizontal image flipping
    def setHFlip(self, flip):
        self.command(bytearray([
            SET,
            VALUE,
            0x61, # LR flip
            0x02 if flip else 0x03
        ]))

    def vFlip(self):
        flip = self.getVFlip()
        self.setVFlip(not flip)

    def hFlip(self):
        flip = self.getHFlip()
        self.setHFlip(not flip)

    #get vertical image flipping
    def getVFlip(self):
        return self.commandRead(bytearray([
            GET,
            VALUE,
            0x66 #picture flip
        ]))[2] == 0x02

    #get horizontal image flipping
    def getHFlip(self):
        return self.commandRead(bytearray([
            GET,
            VALUE,
            0x61 #LR flip
        ]))[2] == 0x02

    def zoom(self, value):
        #value from 0x00 > 0x4000
        self.command(bytearray([
            SET,
            VALUE,
            0x47,
            value >> 12 & 0x0F,
            value >> 8 & 0x0F,
            value >> 4 & 0x0F,
            value & 0x0F
        ]))

    def getPower(self):
        ret = self.commandRead(bytearray([GET, VALUE, 0x00]))
        return ret[2] == 0x02

    def setPower(self, power):
        self.command(bytearray([SET, VALUE, 0x00, 0x02 if power else 0x03]))
        return

    def togglePower(self):
        self.setPower(not self.getPower())
        return

    def recallPreset(self, n):
        self.command(bytearray([SET, VALUE, 0x3F, 0x02, n]))
    def setPreset(self, n):
        self.command(bytearray([SET, VALUE, 0x3F, 0x01, n]))
    def delPreset(self, n):
        self.command(bytearray([SET, VALUE, 0x3F, 0x00, n]))

    def test(self):
        self.command(bytearray([SET, VALUE, 0x00, 0x02]))
        time.sleep(0.5)
        return self.getPower()
