# CrcFinder

A tool to find well known crc params that matches the input data and crc result (right or wrong)

## Install

```bash
pip install crcFinder
```

## Usage

### As Library

#### find `zlib.crc32`

```python
from crcFinder import CrcFinder
import zlib

data = []
data.append((b"123456789", zlib.crc32(b'123456789')))
data.append((b"123456789xxxx", zlib.crc32(b'123456789xxxx')))
f = CrcFinder()
r = f.findCrc(data)
print([str(i) for i in r])
```

#### find something else

```python
from crcFinder import CrcFinder
data = []
data.append((b"123456789\x09", b'\x11\x60\x7a\x37'))
data.append((b"1234567890\x0a", b'\xb3\x95\xcb\x46'))
f = CrcFinder()
r = f.findCrc(data)
print(r[0])
```

#### use CrcCalculator directly

```python
from crcFinder import CrcCalculator, ShiftType
crc_pkzip = CrcCalculator(32, 0x04c11db7, 0xffffffff, True, True, 0xffffffff, ShiftType.LEFT, ShiftType.LEFT)
assert(crc_pkzip.check() == 0xcbf43926)
```

#### Solver
see `tests/test_Solver.py`

### cli

```bash
# find crc poly and other params
python -m crcFinder find -d 616263646566,4b8e39ef
python -m crcFinder find -d 616263646566,0x4b8e39ef 313233343536373839,0xcbf43926
# calculate data crc
python -m crcFinder calculate --params "width=32 poly=0x04c11db7 init=0xffffffff refin=True refout=True xorout=0xffffffff check=0xcbf43926 name=None tableGenShiftType:ShiftType.LEFT calcShiftType:ShiftType.LEFT extra=None" -d 313233343536373839
# generate a padding to data for specified crc checksum value
python -m crcFinder solve --params "width=32 poly=0x04c11db7 init=0xffffffff refin=True refout=True xorout=0xffffffff check=0xcbf43926 name=None tableGenShiftType:ShiftType.LEFT calcShiftType:ShiftType.LEFT extra=None" --data 68656c6c6f --target 0x12345678
```

## Reference

- <https://reveng.sourceforge.io/crc-catalogue/all.htm>
- <https://github.com/Michaelangel007/crc32>
