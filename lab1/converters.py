from bit_array import BitArray

class NumberConverter:
    BIT_LIMIT = 32
    SIGN_INDEX = 0
    INTEGER_BITS = 15
    FRACTION_BITS = 16

    # ---------- Целые числа: прямой, обратный, дополнительный ----------
    @staticmethod
    def decimal_to_direct(value):
        bits = [0] * 32
        bits[0] = 1 if value < 0 else 0
        abs_val = abs(value)
        for i in range(31, 0, -1):
            bits[i] = abs_val % 2
            abs_val //= 2
        return BitArray(bits)

    @staticmethod
    def direct_to_decimal(bit_array):
        bits = bit_array.bits
        mag = 0
        for i in range(1, 32):
            mag = (mag << 1) | bits[i]
        return -mag if bits[0] else mag

    @staticmethod
    def decimal_to_reverse(value):
        bits = NumberConverter.decimal_to_direct(value).bits[:]
        if value < 0:
            for i in range(1, 32):
                bits[i] = 1 - bits[i]
        return BitArray(bits)

    @staticmethod
    def decimal_to_additional(value):
        if value == -2147483648:
            bits = [0] * 32
            bits[0] = 1
            return BitArray(bits)
        bits = NumberConverter.decimal_to_reverse(value).bits[:]
        if value < 0:
            carry = 1
            for i in range(31, 0, -1):
                s = bits[i] + carry
                bits[i] = s % 2
                carry = s // 2
        return BitArray(bits)

    @staticmethod
    def additional_to_decimal(bit_array):
        bits = bit_array.bits
        if bits == [1] + [0] * 31:
            return -2147483648
        is_neg = bits[0] == 1
        working = bits[:]
        if is_neg:
            borrow = 1
            for i in range(31, 0, -1):
                diff = working[i] - borrow
                if diff < 0:
                    working[i] = 1
                    borrow = 1
                else:
                    working[i] = diff
                    borrow = 0
            for i in range(1, 32):
                working[i] = 1 - working[i]
        mag = 0
        for i in range(1, 32):
            mag = (mag << 1) | working[i]
        return -mag if is_neg else mag

    # ---------- Фиксированная точка ----------
    @staticmethod
    def decimal_to_fixed(value):
        bits = [0] * 32
        bits[0] = 1 if value < 0 else 0
        abs_val = abs(value)
        int_part = int(abs_val)
        frac_part = abs_val - int_part
        for i in range(NumberConverter.INTEGER_BITS, 0, -1):
            bits[i] = int_part % 2
            int_part //= 2
        for i in range(NumberConverter.INTEGER_BITS + 1, 32):
            frac_part *= 2
            bit = int(frac_part)
            bits[i] = bit
            frac_part -= bit
        return BitArray(bits)

    @staticmethod
    def fixed_to_decimal(bit_array):
        bits = bit_array.bits
        int_val = 0
        for i in range(1, NumberConverter.INTEGER_BITS + 1):
            int_val = (int_val << 1) | bits[i]
        frac_val = 0.0
        for i in range(NumberConverter.INTEGER_BITS + 1, 32):
            if bits[i]:
                frac_val += 2.0 ** (-(i - NumberConverter.INTEGER_BITS))
        result = int_val + frac_val
        return -result if bits[0] else result

    # ---------- IEEE-754 single precision ----------
    @staticmethod
    def float_to_ieee754(value):
        if value == 0.0:
            return BitArray([0]*32)
        bits = [0]*32
        bits[0] = 1 if value < 0 else 0
        abs_val = abs(value)
        # Нормализация: abs_val = m * 2^e, где 1 <= m < 2
        e = 0
        m = abs_val
        while m >= 2.0:
            m /= 2.0
            e += 1
        while m < 1.0:
            m *= 2.0
            e -= 1
        biased_exp = e + 127
        for i in range(8):
            bits[1+i] = (biased_exp >> (7-i)) & 1
        m -= 1.0
        for i in range(23):
            m *= 2.0
            bit = int(m)
            bits[9+i] = bit
            m -= bit
        return BitArray(bits)

    @staticmethod
    def ieee754_to_float(bit_array):
        bits = bit_array.bits
        sign = -1.0 if bits[0] else 1.0
        exp = 0
        for i in range(8):
            exp = (exp << 1) | bits[1+i]
        mant = 0
        for i in range(23):
            mant = (mant << 1) | bits[9+i]
        if exp == 0:
            if mant == 0:
                return 0.0
            else:
                return sign * (mant / 2**23) * (2 ** -126)
        if exp == 255:
            return float('inf') if mant == 0 else float('nan')
        return sign * (1 + mant / 2**23) * (2 ** (exp - 127))