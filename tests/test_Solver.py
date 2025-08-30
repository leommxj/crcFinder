from crcFinder import CrcCalculator, ShiftType, Solver


def test_padding_crc32_to_target():
    calc = CrcCalculator(32, 0x04c11db7, 0xffffffff, True, True, 0xffffffff, ShiftType.LEFT, ShiftType.LEFT)
    solver = Solver(calc)
    data = b"hello crc"
    target = calc.calculate(b"target data")
    pad = solver.solve_to_target(data, target)
    assert calc.calculate(data + pad) == target


def test_padding_crc32_equal():
    calc = CrcCalculator(32, 0x04c11db7, 0xffffffff, True, True, 0xffffffff, ShiftType.LEFT, ShiftType.LEFT)
    solver = Solver(calc)
    a = b"foo"
    b = b"barbaz"
    pad = solver.solve_equal(a, b)
    assert calc.calculate(a + pad) == calc.calculate(b)


def test_solver_class_api():
    calc = CrcCalculator(32, 0x04c11db7, 0xffffffff, True, True, 0xffffffff, ShiftType.LEFT, ShiftType.LEFT)
    solver = Solver(calc)
    data = b"abc"
    other = b"xyz123"
    pad = solver.solve_equal(data, other)
    assert calc.calculate(data + pad) == calc.calculate(other)

