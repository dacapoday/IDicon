#!/usr/bin/env python3

import zlib
import struct


class PNGCanvas:
    def __init__(self, width, height, size=10, bgcolor=bytearray([0xff, 0xff, 0xff]), color=bytearray([0, 0, 0])):
        self.width = width
        self.height = height
        self.size = size
        self.color = color  # rgb
        self.bgcolor = bgcolor  # rgb
        self.canvas = bytearray(self.bgcolor * 3 * width * height)

    def point(self, x, y, color=None):
        if x < 0 or y < 0 or x > self.size-1 or y > self.size-1:
            return
        if color == None:
            color = self.color
        o = y*self.width*3+x*3
        self.canvas[o:o+3] = color

    def block(self, x, y, color=None):
        if x < 0 or y < 0 or x > self.size-1 or y > self.size-1:
            return
        if color == None:
            color = self.color
        by, bx = int(y*self.width/self.size), int(x*self.height/self.size)
        ey, ex = int((y+1)*self.width/self.size), int((x+1)
                                                      * self.height/self.size)
        o = by*self.width*3+bx*3
        for n in range(ey-by):
            self.canvas[o:o+3*(ex-bx)] = color*(ex-bx)
            o += self.width*3

    def draw(self, code):
        part = self.size
        for y in range(part):
            for x in range(int(part/2)):
                if bin(hash(code))[-int(part/2)*y-x-3] == '1':
                    self.block(4-x, y)
                    self.block(5+x, y)

    def pack_chunk(self, tag, data):  
        # PNG数据块打包
        to_check = tag.encode('ascii') + data
        return struct.pack("!I", len(data)) + to_check + struct.pack("!I", zlib.crc32(to_check) & 0xFFFFFFFF)

    def dump(self):
        scanlines = bytearray()
        for y in range(self.height):
            scanlines.append(0)
            scanlines.extend(
                self.canvas[(y * self.width * 3):((y+1) * self.width * 3)])
        # PNG格式头
        return struct.pack("8B", 137, 80, 78, 71, 13, 10, 26, 10) + \
            self.pack_chunk('IHDR', struct.pack("!2I5B", self.width, self.height, 8, 2, 0, 0, 0)) + \
            self.pack_chunk('IDAT', zlib.compress(bytes(scanlines), 9)) + \
            struct.pack("!I8B", 0, 49, 45, 78, 44, 174, 42, 60, 82)
        # PNG格式尾IEND


def IDicon(width, height, code, size=10):
    col = hex(hash(code))
    color = bytearray(
        [int(col[-9:-7], 16), int(col[-13:-11], 16), int(col[-11:-9], 16)])
    bgcolor = bytearray([0xff-int(col[-7:-5], 16), 0xff -
                         int(col[-3:-1], 16), 0xff-int(col[-5:-3], 16)])
    icon = PNGCanvas(width, height, bgcolor=bgcolor, color=color)
    icon.draw(code)
    return icon.dump()


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('err:too short')
        raise SystemExit
    nun = str(sys.argv)
    width = 73
    height = 73
    print("Creating Canvas...")
    ID = IDicon(width, height, nun)
    print("Writing to file...")
    with open("test.png", "wb") as f:
        f.write(ID)
