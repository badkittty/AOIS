class BitOperations:
    @staticmethod
    def add_bits(a, b):
        result = [0] * 32
        carry = 0
        for i in range(31, -1, -1):
            s = a[i] + b[i] + carry
            result[i] = s % 2
            carry = s // 2
        return result, carry

    @staticmethod
    def invert_bits(bits):
        """Побитовая инверсия (логическое НЕ)."""
        return [1 - bit for bit in bits]

    @staticmethod
    def shift_left(bits, fill=0):
        """Сдвиг влево на 1 разряд с заполнением справа fill."""
        return bits[1:] + [fill]

    @staticmethod
    def compare_registers(a, b):
        """
        Сравнение двух списков битов одинаковой длины как беззнаковых целых.
        Возвращает 1, если a > b; 0, если a == b; -1, если a < b.
        """
        for x, y in zip(a, b):
            if x != y:
                return 1 if x > y else -1
        return 0

    @staticmethod
    def sub_register(a, b):
        """
        Вычитание b из a как беззнаковых целых.
        Предполагается a >= b.
        """
        result = a[:]
        borrow = 0
        for i in range(len(a)-1, -1, -1):
            diff = result[i] - b[i] - borrow
            if diff < 0:
                result[i] = diff + 2
                borrow = 1
            else:
                result[i] = diff
                borrow = 0
        return result