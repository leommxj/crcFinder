import argparse
from crcFinder import CrcFinder

def main():
    parser = argparse.ArgumentParser(prog='crcFinder', formatter_class=argparse.RawDescriptionHelpFormatter, description='eg.\ncrcFinder -d 616263646566,0x4b8e39ef 313233343536373839,0xcbf43926\ncrcFinder -d 616263646566,4b8e39ef')
    parser.add_argument('-d','--data', nargs='+', help='<Required> data and crc in "data,crc" format', required=True)
    args = parser.parse_args()
    input = []
    for d in args.data:
        try:
            data, crc = d.split(',')
            data = bytes.fromhex(data)
            if crc.startswith('0x'):
                crc = int(crc, 16)
            else:
                crc = bytes.fromhex(crc)
            input.append((data, crc))
        except Exception:
            raise ValueError('data and crc format not right')
    f = CrcFinder()
    r = f.findCrc(input)
    if len(r) > 0:
        print([str(i) for i in r])
    else:
        print("no luck")


main()