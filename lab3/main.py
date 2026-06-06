"""Лабораторная работа №3 — вариант 3Еа1.

Часть 1: ОДС-3 (полный сумматор), выходы в СКНФ, масштабирование до 8 разрядов.
Часть 2: преобразователь Gray BCD -> Gray BCD + 1 (вариант Е, смещение n=1).
Автомат:  суммирующий счётчик на 8 состояний на T-триггерах.
"""

from logic import adder3, counter, gray_bcd


def main() -> None:
    print("=" * 60)
    print("ЛР №3, вариант 3Еа1")
    print("=" * 60)
    print("\n[Часть 1]")
    print(adder3.describe())
    print("\n[Часть 2]")
    print(gray_bcd.describe())
    print("\n[Цифровой автомат]")
    print(counter.describe())


if __name__ == "__main__":
    main()
