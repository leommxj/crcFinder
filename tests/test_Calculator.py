from crcFinder import CrcCalculator, ShiftType

def test_valid32():
    crc32_bzip2 = CrcCalculator(32, 0x04c11db7, 0xffffffff, False, False, 0xffffffff, ShiftType.LEFT, ShiftType.LEFT)
    assert(crc32_bzip2.check() == 0xfc891918)

    crc32_bzip2_reflected = CrcCalculator(32, CrcCalculator.reflectBits(0x04c11db7, 32), 0xffffffff, True, True, 0xffffffff, ShiftType.RIGHT, ShiftType.RIGHT)
    assert(crc32_bzip2_reflected.check() == 0xfc891918)

    crc_pkzip = CrcCalculator(32, 0x04c11db7, 0xffffffff, True, True, 0xffffffff, ShiftType.LEFT, ShiftType.LEFT)
    assert(crc_pkzip.check() == 0xcbf43926)


def test_wrong():
    crc_bzip2_wrong1 = CrcCalculator(32, 0x04c11db7, 0xffffffff, False, True, 0xffffffff, ShiftType.LEFT, ShiftType.LEFT)
    assert(crc_bzip2_wrong1.check() == 0x1898913f)

    crc_bzip2_wrong2 = CrcCalculator(32, 0x04c11db7, 0xffffffff, True, False, 0xffffffff, ShiftType.LEFT, ShiftType.LEFT)
    assert(crc_bzip2_wrong2.check() == 0x649C2FD3)

    crc_bzip2_wrong3 = CrcCalculator(32, 0x04c11db7, 0xffffffff, False, False, 0xffffffff, ShiftType.LEFT, ShiftType.RIGHT)
    assert(crc_bzip2_wrong3.check() == 0x7EAD5C77)

    crc_bzip2_wrong4 = CrcCalculator(32, 0x04c11db7, 0xffffffff, False, True, 0xffffffff, ShiftType.LEFT, ShiftType.RIGHT)
    assert(crc_bzip2_wrong4.check() == 0xEE3AB57E)

    crc_bzip2_wrong5 = CrcCalculator(32, 0x04c11db7, 0xffffffff, True, False, 0xffffffff, ShiftType.LEFT, ShiftType.RIGHT)
    assert(crc_bzip2_wrong5.check() == 0x0D0B7023)

    crc_bzip2_wrong6 = CrcCalculator(32, 0x04c11db7, 0xffffffff, True, True, 0xffffffff, ShiftType.LEFT, ShiftType.RIGHT)
    assert(crc_bzip2_wrong6.check() == 0xC40ED0B0)

    crc_bzip2_wrong7 = CrcCalculator(32, 0x04c11db7, 0xffffffff, False, False, 0xffffffff, ShiftType.RIGHT, ShiftType.LEFT)
    assert(crc_bzip2_wrong7.check() == 0xC9A0B7E5)

    crc_bzip2_wrong8 = CrcCalculator(32, 0x04c11db7, 0xffffffff, False, True, 0xffffffff, ShiftType.RIGHT, ShiftType.LEFT)
    assert(crc_bzip2_wrong8.check() == 0xA7ED0593)

    crc_bzip2_wrong9 = CrcCalculator(32, 0x04c11db7, 0xffffffff, True, False, 0xffffffff, ShiftType.RIGHT, ShiftType.LEFT)
    assert(crc_bzip2_wrong9.check() == 0x9D594C04)
    
    crc_bzip2_wrong10 = CrcCalculator(32, 0x04c11db7, 0xffffffff, True, True, 0xffffffff, ShiftType.RIGHT, ShiftType.LEFT)
    assert(crc_bzip2_wrong10.check() == 0x20329AB9)

    crc_bzip2_wrong11 = CrcCalculator(32, 0x04c11db7, 0xffffffff, False, False, 0xffffffff, ShiftType.RIGHT, ShiftType.RIGHT)
    assert(crc_bzip2_wrong11.check() == 0xFC4F2BE9)

    crc_bzip2_wrong12 = CrcCalculator(32, 0x04c11db7, 0xffffffff, False, True, 0xffffffff, ShiftType.RIGHT, ShiftType.RIGHT)
    assert(crc_bzip2_wrong12.check() == 0x97D4F23F)

    crc_bzip2_wrong13 = CrcCalculator(32, 0x04c11db7, 0xffffffff, True, False, 0xffffffff, ShiftType.RIGHT, ShiftType.RIGHT)
    assert(crc_bzip2_wrong13.check() == 0xFDEFB72E)

    crc_bzip2_wrong14 = CrcCalculator(32, 0x04c11db7, 0xffffffff, True, True, 0xffffffff, ShiftType.RIGHT, ShiftType.RIGHT)
    assert(crc_bzip2_wrong14.check() == 0x74EDF7BF)


def test_valid():
    crc8_gsmb = CrcCalculator(8, 0x49, 0x0, False, False, 0xff, ShiftType.LEFT, ShiftType.LEFT)
    assert(crc8_gsmb.check() == 0x94)

    crc10_ATM = CrcCalculator(10, 0x233, 0x0, False, False, 0x0, ShiftType.LEFT, ShiftType.LEFT)
    assert(crc10_ATM.check() == 0x199)

    crc31_PHILIPS = CrcCalculator(31, 0x04c11db7, 0x7fffffff, False, False, 0x7fffffff, ShiftType.LEFT, ShiftType.LEFT)
    assert(crc31_PHILIPS.check() == 0x0ce9e46c)

    crc64_goiso = CrcCalculator(64, 0x1b, 0xffffffffffffffff, True, True, 0xffffffffffffffff, ShiftType.LEFT, ShiftType.LEFT)
    assert(crc64_goiso.check() == 0xb90956c775a41001)