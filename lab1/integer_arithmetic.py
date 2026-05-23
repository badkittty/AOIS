
from bit_array import BitArray
from bit_operations import BitOperations
from converters import NumberConverter

class IntegerArithmetic:
    def __init__(self):
        self.conv = NumberConverter()
        self.ops = BitOperations()

    def add_additional(self, a_dec, b_dec):
        """Сложение в дополнительном коде: (a + b) по модулю 2^32."""
        a_bits = self.conv.decimal_to_additional(a_dec).bits
        b_bits = self.conv.decimal_to_additional(b_dec).bits
        sum_bits, _ = self.ops.add_bits(a_bits, b_bits)
        return BitArray(sum_bits), self.conv.additional_to_decimal(BitArray(sum_bits))

    def negate_additional(self, value):
        """Отрицание в дополнительном коде: -value = (2^32 - value) mod 2^32."""
        if value == -2147483648:
            return value
        bits = self.conv.decimal_to_additional(value).bits
        inverted = self.ops.invert_bits(bits)
        one = [0]*32
        one[31] = 1
        neg_bits, _ = self.ops.add_bits(inverted, one)
        return self.conv.additional_to_decimal(BitArray(neg_bits))

    def subtract_additional(self, a_dec, b_dec):
        return self.add_additional(a_dec, self.negate_additional(b_dec))

    def multiply_direct(self, a_dec, b_dec):
        """Умножение в прямом коде: знак = XOR знаков, модули перемножаются столбиком."""
        sign = 1 if (a_dec < 0) ^ (b_dec < 0) else 0
        a_bits = self.conv.decimal_to_direct(abs(a_dec)).bits
        b_bits = self.conv.decimal_to_direct(abs(b_dec)).bits
        result = [0] * 32
        for i in range(31, 0, -1):
            if b_bits[i]:
                shift = 31 - i
                shifted = a_bits[:]
                for _ in range(shift):
                    shifted = self.ops.shift_left(shifted)
                result, _ = self.ops.add_bits(result, shifted)
        result[0] = sign
        return BitArray(result), self.conv.direct_to_decimal(BitArray(result))

    def divide_direct(self, dividend, divisor):

        if divisor == 0:
            raise ZeroDivisionError("Деление на ноль")
        sign = 1 if (dividend < 0) ^ (divisor < 0) else 0
        abs_div = abs(dividend)
        abs_sor = abs(divisor)
        scale = 32  # 2^5
        quotient = (abs_div * scale) // abs_sor
        int_part = quotient // scale
        frac_part = quotient % scale
        bits = [0] * 32
        bits[0] = sign
        for i in range(15):
            bits[15 - i] = (int_part >> i) & 1
        for i in range(5):
            bits[16 + i] = (frac_part >> (4 - i)) & 1
        dec_result = int_part + frac_part / scale
        if sign:
            dec_result = -dec_result
        return BitArray(bits), dec_result