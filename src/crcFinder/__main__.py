import argparse
import re
from crcFinder import CrcFinder, Solver, CrcCalculator, ShiftType

def _parse_finder_params(params: str) -> CrcCalculator:
    s = params
    def _search(pattern: str) -> str:
        m = re.search(pattern, s)
        if not m:
            raise ValueError('invalid params string')
        return m.group(1)
    width = int(_search(r"width=(\d+)"))
    poly = int(_search(r"poly=0x([0-9a-fA-F]+)"), 16)
    init = int(_search(r"init=0x([0-9a-fA-F]+)"), 16)
    refin = _search(r"refin=(True|False)") == 'True'
    refout = _search(r"refout=(True|False)") == 'True'
    xorout = int(_search(r"xorout=0x([0-9a-fA-F]+)"), 16)
    table_s = _search(r"tableGenShiftType:ShiftType\.(LEFT|RIGHT)")
    calc_s = _search(r"calcShiftType:ShiftType\.(LEFT|RIGHT)")
    table = ShiftType.LEFT if table_s == 'LEFT' else ShiftType.RIGHT
    calc_shift = ShiftType.LEFT if calc_s == 'LEFT' else ShiftType.RIGHT
    return CrcCalculator(width, poly, init, refin, refout, xorout, table, calc_shift)

def main():
    parser = argparse.ArgumentParser(
        prog='crcFinder',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='subcommands: find | calculate | solve\n\n'
                    'examples:\n'
                    '  python -m crcFinder find -d 313233343536373839,0xcbf43926\n'
                    '  python -m crcFinder calculate --params "width=32 poly=0x04c11db7 init=0xffffffff refin=True refout=True xorout=0xffffffff check=0xcbf43926 name=None tableGenShiftType:ShiftType.LEFT calcShiftType:ShiftType.LEFT extra=None" -d 313233343536373839\n'
                    '  python -m crcFinder solve --params "width=32 poly=0x04c11db7 init=0xffffffff refin=True refout=True xorout=0xffffffff check=0xcbf43926 name=None tableGenShiftType:ShiftType.LEFT calcShiftType:ShiftType.LEFT extra=None" --data 68656c6c6f --target 0x12345678\n'
    )
    subparsers = parser.add_subparsers(dest='cmd', required=True)

    # find
    p_find = subparsers.add_parser('find', help='find CRC parameters from samples')
    p_find.add_argument('-d','--data', nargs='+', required=True, help='data and crc in "data,crc" format')

    # calculate (gen)
    p_calc = subparsers.add_parser('calculate', help='calculate CRC using finder-format param string')
    p_calc.add_argument('--params', required=True, help='finder output string of CrcCalculator')
    p_calc.add_argument('-d','--data', nargs='+', required=True, help='hex strings for data inputs')

    # solve (collision/padding)
    p_solve = subparsers.add_parser('solve', help='solve padding for target')
    p_solve.add_argument('--data', required=True, help='hex string of data')
    p_solve.add_argument('--target', required=True, help='target CRC in hex, e.g. 0x12345678')
    p_solve.add_argument('--pad-len', type=int)
    # calculator params for solve (finder style only)
    p_solve.add_argument('--params', required=True, help='finder output string of CrcCalculator')

    args = parser.parse_args()

    if args.cmd == 'find':
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

    elif args.cmd == 'calculate':
        calculator = _parse_finder_params(args.params)
        outs = []
        for h in args.data:
            data = bytes.fromhex(h)
            outs.append(hex(calculator.calculate(data)))
        print(outs)

    elif args.cmd == 'solve':
        calculator = _parse_finder_params(args.params)
        solver = Solver(calculator)
        data = bytes.fromhex(args.data)
        target = int(args.target, 16)
        padding = solver.solve_to_target(data, target, args.pad_len)
        print(padding.hex())


main()