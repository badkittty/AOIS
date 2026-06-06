"""Синтез цифрового автомата, вариант 1.

Двоичный счётчик накапливающего (суммирующего) типа на 8 внутренних
состояний, построенный на T-триггерах. Базис реализации — НЕ, И, ИЛИ.

Для T-триггера справедливо: Q(t+1) = Q(t) XOR T. Отсюда требуемое значение
входа триггера в каждом разряде: T_i = Q_i(t) XOR Q_i(t+1). Следующее
состояние при суммирующем счёте — (state + 1) mod 8.
"""

from __future__ import annotations

from logic.qmc import Row, minimize

STATE_NAMES = ("q2", "q1", "q0")
MODULO = 8
TRIGGERS = ("T2", "T1", "T0")


def _bits(value: int) -> tuple[int, ...]:
    return tuple((value >> (2 - i)) & 1 for i in range(3))


def _trigger_value(state: int, index: int) -> int:
    """Значение входа T триггера разряда index при переходе state -> state+1."""
    nxt = (state + 1) % MODULO
    cur_bit = (state >> (2 - index)) & 1
    nxt_bit = (nxt >> (2 - index)) & 1
    return cur_bit ^ nxt_bit


def trigger_table(index: int) -> list[Row]:
    rows: list[Row] = []
    for state in range(MODULO):
        rows.append(Row(_bits(state), _trigger_value(state, index)))
    return rows


def trigger_formulas() -> dict[str, str]:
    return {
        name: minimize(trigger_table(i), STATE_NAMES, as_dnf=True)
        for i, name in enumerate(TRIGGERS)
    }


def transition_sequence() -> list[int]:
    """Полная последовательность состояний счётчика начиная с 0."""
    seq = [0]
    for _ in range(MODULO):
        seq.append((seq[-1] + 1) % MODULO)
    return seq


def describe() -> str:
    lines = ["Суммирующий счётчик на 8 состояний (T-триггеры), функции входов в СДНФ:"]
    for name, formula in trigger_formulas().items():
        lines.append(f"  {name} = {formula}")
    lines.append("  Последовательность состояний: " +
                 " -> ".join(str(s) for s in transition_sequence()))
    return "\n".join(lines)


if __name__ == "__main__":
    print(describe())
