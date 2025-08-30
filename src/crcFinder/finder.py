from dataclasses import dataclass
from itertools import product
from typing import Union
import logging

from .calculator import CrcCalculator, ShiftType


@dataclass
class WellKnownCrcParams:
    width: int
    poly: int
    init: int = 0
    xorOut: int = 0
    name: str|list|None = None


class CrcFinder:
    # from https://reveng.sourceforge.io/crc-catalogue/all.htm
    WELL_KNOWN_CRC_PARAMS = [
        # 3 4 5 6 7
        WellKnownCrcParams(8, 0x07),
        WellKnownCrcParams(8, 0x31),
        WellKnownCrcParams(8, 0x1D),
        WellKnownCrcParams(8, 0x49),
        WellKnownCrcParams(8, 0x2F),
        WellKnownCrcParams(8, 0x39),
        WellKnownCrcParams(8, 0xD5),
        WellKnownCrcParams(8, 0x9B),
        WellKnownCrcParams(8, 0xA7),
        WellKnownCrcParams(10, 0x3D9),
        WellKnownCrcParams(10, 0x175),
        WellKnownCrcParams(10, 0x233),
        # 11 12 13 14 15
        WellKnownCrcParams(16, 0x0589),
        WellKnownCrcParams(16, 0x080B),
        WellKnownCrcParams(16, 0x1021),
        WellKnownCrcParams(16, 0x1DCF),
        WellKnownCrcParams(16, 0x3D65),
        WellKnownCrcParams(16, 0x8005),
        WellKnownCrcParams(16, 0x5935),
        WellKnownCrcParams(16, 0x6F63),
        WellKnownCrcParams(16, 0x755B),
        WellKnownCrcParams(16, 0x8BB7),
        WellKnownCrcParams(16, 0xA097),
        WellKnownCrcParams(16, 0xC867),
        # 17
        WellKnownCrcParams(24, 0x00065B),
        WellKnownCrcParams(24, 0x328B63),
        WellKnownCrcParams(24, 0x5D6DCB),
        WellKnownCrcParams(24, 0x800063),
        WellKnownCrcParams(24, 0x864CFB),
        # 30 31
        WellKnownCrcParams(32, 0x000000AF),
        WellKnownCrcParams(32, 0x04C11DB7),
        WellKnownCrcParams(32, 0x1EDC6F41),
        WellKnownCrcParams(32, 0x741B8CD7),
        WellKnownCrcParams(32, 0x8001801B),
        WellKnownCrcParams(32, 0x814141AB),
        WellKnownCrcParams(32, 0xF4ACFB13),
        WellKnownCrcParams(32, 0xA833982B),
        WellKnownCrcParams(32, 0x9132becd, name='Tenda'),
        WellKnownCrcParams(
            40,
            0x0004820009,
        ),
        WellKnownCrcParams(64, 0x000000000000001B),
        WellKnownCrcParams(64, 0x259C84CBA6426349),
        WellKnownCrcParams(64, 0xAD93D23594C935A9),
        WellKnownCrcParams(64, 0x42F0E1EBA9EA3693),
        # 82
    ]

    def __init__(self):
        pass

    def verifyPoly(
        self, data: bytes, crc: Union[bytes, int], params: WellKnownCrcParams
    ):
        if type(crc) == bytes:
            crc = int(crc.hex(), 16)
        r = []
        init_list = [0, (1 << params.width) - 1]
        if params.init not in init_list:
            init_list.append(params.init)
        refIn_list = [True, False]
        refOut_list = [True, False]
        xorOut_list = [0, (1 << params.width) - 1]
        if params.xorOut not in xorOut_list:
            xorOut_list.append(params.xorOut)
        tableGenShiftType_list = [ShiftType.LEFT, ShiftType.RIGHT]
        calcShiftType_list = [ShiftType.LEFT, ShiftType.RIGHT]
        for brute_things in product(
            init_list,
            refIn_list,
            refOut_list,
            xorOut_list,
            tableGenShiftType_list,
            calcShiftType_list,
        ):
            result = self.verify(
                data,
                crc,
                params.width,
                params.poly,
                brute_things[0],
                brute_things[1],
                brute_things[2],
                brute_things[3],
                brute_things[4],
                brute_things[5],
                params.name
            )
            if result:
                r.append(result)
            else:
                logging.debug(
                    "not hit for width:{} poly:{} brute_things: {}".format(
                        params.width, params.poly, brute_things
                    )
                )
        if len(r) > 0:
            return r
        else:
            return None

    def verify(
        self,
        data: bytes,
        crc: int,
        width: int,
        poly: int,
        init: int,
        refIn: bool,
        refOut: bool,
        xorOut: int,
        tableGenShiftType: ShiftType,
        calcShiftType: ShiftType,
        name: str|list|None
    ):
        mask = (1 << width) - 1
        crc_masked = crc & mask
        if crc_masked != crc:
            return None

        calculator = CrcCalculator(
            width, poly, init, refIn, refOut, xorOut, tableGenShiftType, calcShiftType, name
        )
        result = calculator(data)
        hex_width = 2 * int((width + 7) / 8)
        crc_le = int(
            (
                bytes.fromhex("{:0{hex_width}x}".format(crc, hex_width=hex_width))[::-1]
            ).hex(),
            16,
        )
        if result == crc:
            return calculator
        elif result == crc_le:
            calculator.add_extra("result_is_le")
            return calculator
        return None

    def verifyWithCalculator(
        self, data: bytes, crc: Union[bytes, int], calculator: CrcCalculator
    ):
        if type(crc) == bytes:
            crc = int(crc.hex(), 16)
        result = calculator(data)
        if calculator.extra and "result_is_le" in calculator.extra:
            hex_width = 2 * int((calculator.width + 7) / 8)
            crc_le = int(
                (
                    bytes.fromhex("{:0{hex_width}x}".format(crc, hex_width=hex_width))[
                        ::-1
                    ]
                ).hex(),
                16,
            )
            if result == crc_le:
                return calculator
        else:
            if result == crc:
                return calculator
        return None

    def findCrc(self, datas):
        r = []
        first_iter = True
        for data, crc in datas:
            if first_iter:
                for param in self.WELL_KNOWN_CRC_PARAMS:
                    result = self.verifyPoly(data, crc, param)
                    if result is not None:
                        r += result
                first_iter = False
            else:
                r = [
                    calculator
                    for calculator in r
                    if self.verifyWithCalculator(data, crc, calculator) is not None
                ]
            if len(r) == 0:
                return []
        return r
