"""Часть 1, вариант 3 — одноразрядный двоичный сумматор на 3 входа (ОДС-3).

Входы: a, b, c_in (перенос из младшего разряда).
Выходы: s (сумма) и c_out (перенос в старший разряд).
По условию варианта 3 выходные функции представляем в СКНФ.

Сумматор затем масштабируется до 8 разрядов каскадным соединением
(ripple-carry): перенос каждого разряда подаётся на вход следующего.
"""

from __future__ import annotations

from logic.qmc import Row, build_rows, minimize

INPUT_NAMES = ("a", "b", "c_in")


def _sum_bit(bits: tuple[int, ...]) -> int:
    return sum(bits) & 1


def _carry_bit(bits: tuple[int, ...]) -> int:
    return 1 if sum(bits) >= 2 else 0


def sum_table() -> list[Row]:
    return build_rows(3, _sum_bit)


def carry_table() -> list[Row]:
    return build_rows(3, _carry_bit)


def sum_sknf() -> str:
    return minimize(sum_table(), INPUT_NAMES, as_dnf=False)


def carry_sknf() -> str:
    return minimize(carry_table(), INPUT_NAMES, as_dnf=False)


def add_byte(x: int, y: int) -> tuple[int, int]:
    """Сложение двух 8-разрядных чисел каскадом из восьми ОДС-3.

    Возвращает (результат_8_бит, итоговый_перенос).
    Демонстрирует масштабирование одноразрядной схемы до 8 разрядов.
    """
    if not (0 <= x < 256 and 0 <= y < 256):
        raise ValueError("Операнды должны укладываться в 8 разрядов (0..255)")

    carry = 0
    result = 0
    for pos in range(8):
        a = (x >> pos) & 1
        b = (y >> pos) & 1
        bits = (a, b, carry)
        s = _sum_bit(bits)
        carry = _carry_bit(bits)
        result |= s << pos
    return result & 0xFF, carry


def describe() -> str:
    lines = [
        "ОДС-3 (полный сумматор), выходные функции в СКНФ:",
        f"  S      = {sum_sknf()}",
        f"  C_out  = {carry_sknf()}",
        "",
        "Демонстрация (8-разрядный каскад): 8 + 6",
    ]
    res, c = add_byte(8, 6)
    lines.append(f"  8 + 6 = {res} (двоичн. {res:08b}), перенос = {c}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(describe())
