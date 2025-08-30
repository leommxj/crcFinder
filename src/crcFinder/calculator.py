from enum import Enum
import logging

class ShiftType(Enum):
    RIGHT = 1
    LEFT = 2


class WrongCalcShiftType(Exception):
    pass


class WrongTableGenShiftType(Exception):
    pass


class CrcCalculator():
    def __init__(self, width: int, poly: int, init: int, refIn: bool, refOut: bool, xorOut: int, tableGenShiftType: ShiftType, calcShiftType: ShiftType, name:str = None, extra: str = None):
        self.width = width
        self.mask = (1<<width) - 1 
        self.poly = poly
        self.init = init
        self.refIn = refIn
        self.refOut = refOut
        self.xorOut = xorOut
        self.name = name
        self.extra = extra
        self.calcShiftType = calcShiftType
        if calcShiftType == ShiftType.RIGHT:
            self.calc = self.calcRight
        elif calcShiftType == ShiftType.LEFT:
            self.calc = self.calcLeft
        else:
            raise WrongCalcShiftType()
        self.tableGenShiftType = tableGenShiftType
        if tableGenShiftType == ShiftType.RIGHT:
                self.genTableRight()
        elif tableGenShiftType == ShiftType.LEFT:
            self.genTableLeft()
        else:
            raise WrongTableGenShiftType()
        logging.debug("table: {}".format(self.table))
        self.reflectBits = self._instance_reflectBits

    def _apply_refin(self, data: bytes) -> bytes:
        if not self.refIn:
            return data
        d = []
        for b in data:
            d.append(int('{:08b}'.format(b)[::-1], 2))
        return bytes(d)

    @staticmethod
    def reflectBits(n: int, width: int) -> int:
        return int('{:0{width}b}'.format(n, width=width)[::-1], 2)

    def _instance_reflectBits(self, n: int) -> int:
        return CrcCalculator.reflectBits(n, self.width)

    def calcRight(self, data: bytes):
        crc = self.init
        for b in data:
            index = (crc ^ b) & 0xFF
            crc = crc >> 8
            crc ^= self.table[index]
        return crc

    def calcLeft(self, data: bytes):
        crc = self.init
        for b in data:
            index = (crc >> (self.width - 8)) ^ b
            crc = (crc << 8) & self.mask
            crc ^= self.table[index]
        return crc

    def _advanceRight(self, state: int, data: bytes) -> int:
        crc = state
        for b in data:
            index = (crc ^ b) & 0xFF
            crc = crc >> 8
            crc ^= self.table[index]
        return crc

    def _advanceLeft(self, state: int, data: bytes) -> int:
        crc = state
        for b in data:
            index = (crc >> (self.width - 8)) ^ b
            crc = (crc << 8) & self.mask
            crc ^= self.table[index]
        return crc

    def genTableRight(self):
        tbl = [None]*256
        for byte in range(0, 256):
            crc = byte
            for _ in range(0, 8):
                c = crc >> 1
                if (crc & 0x1) != 0:
                    crc = c ^ self.poly
                else:
                    crc = c
            tbl[byte] = crc
        self.table = tbl

    def genTableLeft(self):
        tbl = [None]*256
        for byte in range(0, 256):
            crc = byte << (self.width - 8)
            for _ in range(0, 8):
                c = (crc << 1) & self.mask
                if (crc >> (self.width-1)) != 0:
                    crc = c ^ self.poly
                else:
                    crc = c
            tbl[byte] = crc
        self.table = tbl

    def calculate(self, data: bytes) -> int:
        logging.debug("input data: {}".format(data))
        if self.refIn:
            data = self._apply_refin(data)
            logging.debug("input data after reflected: {}".format(data))

        crc = self.calc(data)
        logging.debug("crc result: {:x}".format(crc))

        if self.refOut:
            crc = self.reflectBits(crc)
        return crc ^ self.xorOut

    def calculate_raw(self, data: bytes) -> int:
        """
        计算未应用 refOut/xorOut 的内部寄存器状态（从 init 出发）。
        """
        if self.refIn:
            data = self._apply_refin(data)
        if self.calcShiftType == ShiftType.RIGHT:
            return self._advanceRight(self.init, data)
        else:
            return self._advanceLeft(self.init, data)

    def advance_raw(self, state: int, data: bytes) -> int:
        """
        从给定内部状态继续处理更多字节，返回新的内部状态（未应用 refOut/xorOut）。
        """
        if self.refIn:
            data = self._apply_refin(data)
        if self.calcShiftType == ShiftType.RIGHT:
            return self._advanceRight(state, data)
        else:
            return self._advanceLeft(state, data)

    def finalize_raw(self, state: int) -> int:
        """
        将内部状态应用 refOut/xorOut，得到对外可见的 CRC 值。
        """
        crc = state
        if self.refOut:
            crc = self.reflectBits(crc)
        return crc ^ self.xorOut
    
    def check(self) -> int:
        return self.calculate(b'123456789')
    
    def __call__(self, data) -> int:
        return self.calculate(data)

    def add_extra(self, s: str):
        if self.extra is None:
            self.extra = s
        else:
            self.extra += ',' + s

    def __str__(self):
        return "width={self.width:} poly=0x{self.poly:0{hex_width}x} init=0x{self.init:0{hex_width}x} refin={self.refIn} refout={self.refOut} xorout=0x{self.xorOut:0{hex_width}x} check=0x{check:0{hex_width}x} name={self.name} tableGenShiftType:{self.tableGenShiftType} calcShiftType:{self.calcShiftType} extra={self.extra}".format(self=self, hex_width=2*int((self.width+7)/8), check=self.check())
    
    def __eq__(self, other):
        if str(self) == str(other):
            return True
        else:
            False