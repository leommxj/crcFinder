from typing import List, Tuple, Optional

from .calculator import CrcCalculator


def _ceil_div(a: int, b: int) -> int:
    return (a + b - 1) // b


def _msb_index(x: int) -> int:
    return x.bit_length() - 1


def _compute_influence_columns(
    calculator: CrcCalculator,
    prefix_state: int,
    pad_len: int,
) -> Tuple[List[int], int]:
    zero_pad = bytes([0] * pad_len)
    state_zero = calculator.advance_raw(prefix_state, zero_pad)

    columns: List[int] = []
    for byte_index in range(pad_len):
        for bit_index in range(8):
            test = bytearray([0] * pad_len)
            test[byte_index] = 1 << bit_index
            state_test = calculator.advance_raw(prefix_state, bytes(test))
            col = state_test ^ state_zero
            col &= calculator.mask
            columns.append(col)
    return columns, state_zero


def _build_linear_basis(columns: List[int]) -> Tuple[List[Optional[int]], List[Optional[int]]]:
    basis_vec: List[Optional[int]] = [None] * 128
    basis_comb: List[Optional[int]] = [None] * 128

    for j, v in enumerate(columns):
        if v == 0:
            continue
        comb = 1 << j
        x = v
        while x:
            p = _msb_index(x)
            if basis_vec[p] is None:
                basis_vec[p] = x
                basis_comb[p] = comb
                break
            else:
                x ^= basis_vec[p]
                comb ^= basis_comb[p]  # type: ignore
    return basis_vec, basis_comb


def _represent_with_basis(target: int, basis_vec: List[Optional[int]], basis_comb: List[Optional[int]]) -> Optional[int]:
    x = target
    comb = 0
    while x:
        p = _msb_index(x)
        if basis_vec[p] is None:
            return None
        x ^= basis_vec[p]  # type: ignore
        comb ^= basis_comb[p]  # type: ignore
    return comb


def _comb_to_bytes(comb: int, pad_len: int) -> bytes:
    out = bytearray([0] * pad_len)
    for j in range(pad_len * 8):
        if (comb >> j) & 1:
            byte_index = j // 8
            bit_index = j % 8
            out[byte_index] |= (1 << bit_index)
    return bytes(out)


class Solver:
    def __init__(self, calculator: CrcCalculator):
        self.calculator = calculator

    def solve_to_target(self, data: bytes, target_crc: int, pad_len: Optional[int] = None) -> bytes:
        width = self.calculator.width
        min_len = _ceil_div(width, 8)
        if pad_len is None:
            pad_len = min_len

        prefix_state = self.calculator.calculate_raw(data)

        t = target_crc ^ self.calculator.xorOut
        if self.calculator.refOut:
            target_raw = self.calculator.reflectBits(t)
        else:
            target_raw = t
        target_raw &= self.calculator.mask

        columns, state_zero = _compute_influence_columns(self.calculator, prefix_state, pad_len)
        delta = state_zero ^ target_raw

        basis_vec, basis_comb = _build_linear_basis(columns)
        comb = _represent_with_basis(delta, basis_vec, basis_comb)
        if comb is None:
            raise ValueError(
                f"no solution with pad_len={pad_len}; try pad_len >= {min_len} or increase length"
            )

        padding = _comb_to_bytes(comb, pad_len)
        final_crc = self.calculator.calculate(data + padding)
        if final_crc != target_crc:
            raise RuntimeError("internal error: solved padding did not match target crc")
        return padding

    def solve_equal(self, data: bytes, other: bytes, pad_len: Optional[int] = None) -> bytes:
        target_crc = self.calculator.calculate(other)
        return self.solve_to_target(data, target_crc, pad_len)

