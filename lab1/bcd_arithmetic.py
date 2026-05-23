
class BCDArithmetic:
    @staticmethod
    def decimal_to_excess3(s):
        bits = []
        for ch in s:
            if ch == '-': continue
            val = int(ch) + 3
            for i in range(3, -1, -1):
                bits.append((val >> i) & 1)
        return bits

    @staticmethod
    def excess3_to_decimal(bits):
        value = 0
        for i in range(0, len(bits), 4):
            tetrad = bits[i:i+4]
            excess = 0
            for bit in tetrad:
                excess = (excess << 1) | bit
            value = value * 10 + (excess - 3)
        return value

    @staticmethod
    def add_excess3(a_bits, b_bits):
        # Преобразуем в цифры 0-9
        def bits_to_digits(bits):
            digits = []
            for i in range(0, len(bits), 4):
                val = 0
                for bit in bits[i:i+4]:
                    val = (val << 1) | bit
                digits.append(val - 3)
            return digits

        a_digits = bits_to_digits(a_bits)
        b_digits = bits_to_digits(b_bits)
        max_len = max(len(a_digits), len(b_digits))
        a_digits = [0]*(max_len - len(a_digits)) + a_digits
        b_digits = [0]*(max_len - len(b_digits)) + b_digits

        carry = 0
        res_digits = []
        for i in range(max_len-1, -1, -1):
            s = a_digits[i] + b_digits[i] + carry
            if s >= 10:
                carry = 1
                s -= 10
            else:
                carry = 0
            res_digits.insert(0, s)
        if carry:
            res_digits.insert(0, 1)

        result_bits = []
        for d in res_digits:
            val = d + 3
            for i in range(3, -1, -1):
                result_bits.append((val >> i) & 1)
        return result_bits