class BitArray:
    """Контейнер для 32 битов с удобным выводом."""
    def __init__(self, bits=None):
        self.bits = bits if bits is not None else [0] * 32

    def to_string(self):
        s = ''.join(str(b) for b in self.bits)
        return ' '.join(s[i:i+8] for i in range(0, 32, 8))