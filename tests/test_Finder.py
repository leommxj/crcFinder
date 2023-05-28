from crcFinder import CrcFinder, CrcCalculator, ShiftType

def test_finder():
    f = CrcFinder()
    data = []
    import zlib
    data.append((b"123456789", zlib.crc32(b'123456789')))
    data.append((b"123456789xxxx", zlib.crc32(b'123456789xxxx')))
    r = f.findCrc(data)
    assert(len(r) == 1)
    assert(r[0] == CrcCalculator(32, 0x04c11db7, 0xffffffff, True, True, 0xffffffff, ShiftType.LEFT, ShiftType.LEFT))

    data = []
    data.append((b'123456789', b'\xb0\xd0\x0e\xc4'))
    r = f.findCrc(data)
    assert(len(r) == 1)
    assert(r[0] == CrcCalculator(32, 0x04c11db7, 0xffffffff, True, True, 0xffffffff, ShiftType.LEFT, ShiftType.RIGHT, extra="result_is_le"))