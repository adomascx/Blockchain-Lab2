from __future__ import annotations

import math
import sys
from typing import Iterable

def HashFunction(string: str):
    
    _MASK64 = (1 << 64) - 1

    # 64-bit unsigned constants
    _C1 = 0x9E3779B97F4A7C15
    _C2 = 0xBF58476D1CE4E5B9
    _C3 = 0x94D049BB133111EB

    # Largest finite IEEE-754 double in Python
    _MAX_DOUBLE = sys.float_info.max


    def _u64(x: int) -> int:
        """Force to uint64 domain."""
        return x & _MASK64


    def _mix64(z: int) -> int:
        """SplitMix64-style mixer. All ops in uint64 with logical shifts."""
        z = _u64(z + _C1)
        z = _u64((z ^ (z >> 30)) * _C2)
        z = _u64((z ^ (z >> 27)) * _C3)
        z = z ^ (z >> 31)
        return _u64(z)


    def _hex64(u: int) -> str:
        """16-digit uppercase hex for a uint64."""
        return f"{u & _MASK64:016X}"


    def _safe_abs(v: float) -> float:
        """Return a bounded absolute value, handling NaN and infinities explicitly."""
        if math.isnan(v):
            return 0.0
        if math.isinf(v):
            return _MAX_DOUBLE / 2.0
        return abs(v)


    def _float_to_hex32(input_value_in: float) -> str:
        """
        Deterministic 32-hex digest from a float.
        Matches the pseudocode semantics, including uint64 wrap behavior.
        """
        input_value = _safe_abs(input_value_in)

        # Base-10 exponent component
        if input_value > 0.0:
            exp10 = int(math.floor(math.log10(input_value)))
        else:
            exp10 = 0
            input_value = 0.0

        if input_value > 0.0:
            normalized = input_value / (10.0 ** exp10)  # target in [1, 10)
        else:
            normalized = 0.0

        acc1 = 0  # uint64
        acc2 = 0  # uint64

        # First 24 base-10 digits -> base-11 accumulator
        for _ in range(24):
            d = int(normalized)  # trunc toward zero; typically 0..9
            acc1 = _u64(acc1 * 11 + d)
            normalized = (normalized - d) * 10.0

        # Next 24 base-10 digits -> base-13 accumulator
        for _ in range(24):
            d = int(normalized)
            acc2 = _u64(acc2 * 13 + d)
            normalized = (normalized - d) * 10.0

        # Fold base-10 exponent (two's-complement 16-bit slice)
        exp_component = int(exp10) & 0xFFFF  # low 16 bits of signed exp10
        acc1 ^= (exp_component << 48) & _MASK64
        acc2 ^= (exp_component << 32) & _MASK64

        # Avalanche mix
        acc1 = _mix64(acc1)
        acc2 = _mix64(acc2 ^ acc1)

        # 32 hex chars: acc1 || acc2
        return _hex64(acc1) + _hex64(acc2)


    def pha256(data: bytes | bytearray | memoryview | str | Iterable[int]) -> str:
        """
        PHA256 hash.
        Input:
            - bytes-like, str (encoded as UTF-8), or iterable of ints in [0,255].
        Output:
            - 64 uppercase hex characters.
        """
        # Normalize input to an iterable of byte values 0..255
        if isinstance(data, str):
            buf = data.encode("utf-8")
        elif isinstance(data, (bytes, bytearray, memoryview)):
            buf = bytes(data)
        else:
            # Treat as iterable of ints
            buf = bytes(int(b) & 0xFF for b in data)

    # Initial seed values for the iterative hash state
        x = 0.31830988618379067154  # 1/pi
        y = 0.41421356237309504880  # sqrt(2) - 1
        z = 0.23205080756887729352  # sqrt(3)/3
        phase = 0.0

    # Iterate over each byte in the buffer
        for c in buf:
            angle = float(c) + 37.0 * phase + z * 911.0
            s = math.sin(angle)
            co = math.cos(angle)

            nx = x + co + 0.5 * s * (y - z)
            ny = y + s + 0.5 * co * (z - x)
            nz = z + (s * co) * 0.75 + 0.125 * (x - y)

            x, y, z = nx, ny, nz

            phase = phase + (float(c) * 0.0078125) + ((s * co) * 0.03125)  # c/128 + (s*co)/32
            phase = math.fmod(phase, 1024.0)

    # Compute composite magnitudes for the final digest stage
        mag1 = _safe_abs(x + 0.61803398874989484820 * y + 0.5 * z)
        mag2 = _safe_abs(y - 0.70710678118654752440 * x + 1.25 * z)

        if mag1 == 0.0:
            mag1 = 1e-300
        if mag2 == 0.0:
            mag2 = 1e-300

        # 64-char digest
        return _float_to_hex32(mag1) + _float_to_hex32(mag2)

    return pha256(str(string))