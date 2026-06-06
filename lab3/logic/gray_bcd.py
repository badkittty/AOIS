"""Часть 2, вариант Е (Gray BCD), смещение а) n = 1.

Преобразователь тетрады десятично-двоичного кода в коде Грея (Gray BCD)
в код, увеличенный на n = 1, с результатом в двух разрядах при переполнении.

Десятичная цифра d (0..9) кодируется отражённым кодом Грея. На выходе
получаем d + 1: если сумма < 10 — выводим её в Gray BCD (старшая тетрада 0),
если 9 + 1 = 10 — появляется перенос (старший разряд = 1), а младшая
тетрада кодирует 0.
"""

from __future__ import annotations

from logic.qmc import Row, minimize

INPUT_NAMES = ("x3", "x2", "x1", "x0")
OFFSET = 1

# Отражённый код Грея для десятичных цифр 0..9 (4 бита, MSB первым).
GRAY_BCD = {
    0: (0, 0, 0, 0),
    1: (0, 0, 0, 1),
    2: (0, 0, 1, 1),
    3: (0, 0, 1, 0),
    4: (0, 1, 1, 0),
    5: (0, 1, 1, 1),
    6: (0, 1, 0, 1),
    7: (0, 1, 0, 0),
    8: (1, 1, 0, 0),
    9: (1, 1, 0, 1),
}

# Обратное отображение код -> цифра для разбора входной тетрады.
_DECODE = {bits: digit for digit, bits in GRAY_BCD.items()}

# Имена выходов: перенос и четыре разряда результата в Gray BCD.
OUTPUTS = ("carry", "y3", "y2", "y1", "y0")


def _transform(bits: tuple[int, ...]) -> dict[str, int] | None:
    """Возвращает значения всех выходов для входной тетрады либо None (don't care)."""
    digit = _DECODE.get(bits)
    if digit is None:
        return None  # код не соответствует ни одной десятичной цифре
    total = digit + OFFSET
    carry = total // 10
    low = total % 10
    g3, g2, g1, g0 = GRAY_BCD[low]
    return {"carry": carry, "y3": g3, "y2": g2, "y1": g1, "y0": g0}


def output_table(output: str) -> list[Row]:
    """Таблица истинности для одного из выходов."""
    rows: list[Row] = []
    for code in range(16):
        bits = tuple((code >> (3 - i)) & 1 for i in range(4))
        mapped = _transform(bits)
        out = None if mapped is None else mapped[output]
        rows.append(Row(bits, out))
    return rows


def all_formulas() -> dict[str, str]:
    """Минимизированные (СДНФ) выражения для каждого выхода."""
    return {name: minimize(output_table(name), INPUT_NAMES, as_dnf=True) for name in OUTPUTS}


def describe() -> str:
    lines = ["Преобразователь Gray BCD -> Gray BCD + 1 (СДНФ):"]
    for name, formula in all_formulas().items():
        lines.append(f"  {name} = {formula}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(describe())
