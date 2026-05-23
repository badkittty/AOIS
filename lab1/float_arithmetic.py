from bit_array import BitArray
from converters import NumberConverter

class FloatArithmetic:
    def __init__(self):
        self.conv = NumberConverter()

    @staticmethod
    def _unpack(bits):
        sign = bits[0]
        exp = 0
        for i in range(8):
            exp = (exp << 1) | bits[1+i]
        mant = 0
        for i in range(23):
            mant = (mant << 1) | bits[9+i]
        if exp != 0:
            mant |= (1 << 23)  # неявная единица
        return sign, exp, mant

    @staticmethod
    def _pack(sign, exp, mant):
        bits = [0]*32
        bits[0] = sign
        for i in range(8):
            bits[1+i] = (exp >> (7-i)) & 1
        for i in range(23):
            bits[9+i] = (mant >> (22-i)) & 1
        return bits

    def add_float(self, a, b):
        a_bits = self.conv.float_to_ieee754(a).bits
        b_bits = self.conv.float_to_ieee754(b).bits
        sign_a, exp_a, mant_a = self._unpack(a_bits)
        sign_b, exp_b, mant_b = self._unpack(b_bits)

        if exp_a == 0 and mant_a == 0:
            return BitArray(b_bits), b
        if exp_b == 0 and mant_b == 0:
            return BitArray(a_bits), a

        # Выравнивание порядков: большее число первым
        if exp_a < exp_b:
            sign_a, sign_b = sign_b, sign_a
            exp_a, exp_b = exp_b, exp_a
            mant_a, mant_b = mant_b, mant_a

        shift = exp_a - exp_b
        mant_b_shifted = mant_b >> shift
        if (mant_b & ((1 << shift) - 1)) != 0:
            mant_b_shifted |= 1  # sticky bit

        if sign_a == sign_b:
            mant_sum = mant_a + mant_b_shifted
            result_sign = sign_a
        else:
            if mant_a >= mant_b_shifted:
                mant_sum = mant_a - mant_b_shifted
                result_sign = sign_a
            else:
                mant_sum = mant_b_shifted - mant_a
                result_sign = sign_b

        if mant_sum == 0:
            return BitArray([0]*32), 0.0

        exp_res = exp_a
        while mant_sum >= (1 << 24):
            mant_sum >>= 1
            exp_res += 1
        while mant_sum < (1 << 23):
            mant_sum <<= 1
            exp_res -= 1

        if exp_res >= 255:
            inf_bits = [0]*32
            inf_bits[0] = result_sign
            for i in range(1,9): inf_bits[i] = 1
            return BitArray(inf_bits), float('inf') if result_sign==0 else float('-inf')
        if exp_res <= 0:
            return BitArray([0]*32), 0.0

        mant_out = mant_sum & ((1 << 23) - 1)
        res_bits = self._pack(result_sign, exp_res, mant_out)
        return BitArray(res_bits), self.conv.ieee754_to_float(BitArray(res_bits))

    def subtract_float(self, a, b):
        return self.add_float(a, -b)

    def multiply_float(self, a, b):
        a_bits = self.conv.float_to_ieee754(a).bits
        b_bits = self.conv.float_to_ieee754(b).bits
        sign_a, exp_a, mant_a = self._unpack(a_bits)
        sign_b, exp_b, mant_b = self._unpack(b_bits)

        if (exp_a == 0 and mant_a == 0) or (exp_b == 0 and mant_b == 0):
            return BitArray([0]*32), 0.0

        result_sign = sign_a ^ sign_b
        exp_res = exp_a + exp_b - 127
        product = mant_a * mant_b
        if product >= (1 << 47):
            product >>= 1
            exp_res += 1

        mant_out = (product >> 23) & ((1 << 23) - 1)
        if (product >> 22) & 1:
            mant_out += 1
            if mant_out >= (1 << 23):
                mant_out >>= 1
                exp_res += 1

        if exp_res >= 255:
            inf_bits = [0]*32
            inf_bits[0] = result_sign
            for i in range(1,9): inf_bits[i] = 1
            return BitArray(inf_bits), float('inf') if result_sign==0 else float('-inf')
        if exp_res <= 0:
            return BitArray([0]*32), 0.0

        res_bits = self._pack(result_sign, exp_res, mant_out)
        return BitArray(res_bits), self.conv.ieee754_to_float(BitArray(res_bits))

    def divide_float(self, a, b):
        if b == 0.0:
            raise ZeroDivisionError("Деление на ноль")
        a_bits = self.conv.float_to_ieee754(a).bits
        b_bits = self.conv.float_to_ieee754(b).bits
        sign_a, exp_a, mant_a = self._unpack(a_bits)
        sign_b, exp_b, mant_b = self._unpack(b_bits)

        if exp_a == 0 and mant_a == 0:
            return BitArray([0]*32), 0.0

        result_sign = sign_a ^ sign_b
        exp_res = exp_a - exp_b + 127
        dividend = mant_a << 23
        quotient = dividend // mant_b
        remainder = dividend % mant_b

        if quotient < (1 << 23):
            quotient <<= 1
            exp_res -= 1
        if remainder * 2 >= mant_b:
            quotient += 1

        mant_out = quotient & ((1 << 23) - 1)

        if exp_res >= 255:
            inf_bits = [0]*32
            inf_bits[0] = result_sign
            for i in range(1,9): inf_bits[i] = 1
            return BitArray(inf_bits), float('inf') if result_sign==0 else float('-inf')
        if exp_res <= 0:
            return BitArray([0]*32), 0.0

        res_bits = self._pack(result_sign, exp_res, mant_out)
        return BitArray(res_bits), self.conv.ieee754_to_float(BitArray(res_bits))