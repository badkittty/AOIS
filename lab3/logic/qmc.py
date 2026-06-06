"""Минимизация булевых функций методом Квайна — Мак-Класки.

Модуль реализует поиск простых импликант через итеративное склеивание
наборов, отличающихся в одном разряде, и последующий выбор минимального
покрытия (ядровые импликанты + жадное добор оставшихся).

Функция задаётся таблицей истинности: каждая строка — это кортеж
``(значения_аргументов, выход)``, где выход принадлежит {0, 1, None}.
None трактуется как безразличное состояние (don't care).
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable, Optional, Sequence

# Символ, обозначающий «разряд исключён при склеивании».
WILDCARD = "-"


@dataclass(frozen=True)
class Row:
    """Одна строка таблицы истинности."""

    args: tuple[int, ...]
    out: Optional[int]

    @property
    def pattern(self) -> str:
        return "".join(str(b) for b in self.args)


def build_rows(width: int, evaluator) -> list[Row]:
    """Перебирает все 2**width наборов и формирует таблицу.

    ``evaluator`` получает кортеж битов и возвращает 0, 1 или None.
    """
    rows: list[Row] = []
    for code in range(1 << width):
        bits = tuple((code >> (width - 1 - i)) & 1 for i in range(width))
        rows.append(Row(bits, evaluator(bits)))
    return rows


def _selected_patterns(rows: Sequence[Row], want_one: bool, with_dc: bool) -> list[str]:
    """Отбирает наборы, участвующие в минимизации.

    Для ДНФ берём строки с выходом 1, для КНФ — с выходом 0.
    При with_dc=True дополнительно подхватываем безразличные наборы.
    """
    goal = 1 if want_one else 0
    chosen: list[str] = []
    for r in rows:
        if r.out == goal or (with_dc and r.out is None):
            chosen.append(r.pattern)
    return chosen


def _single_mismatch(left: str, right: str) -> int:
    """Возвращает позицию единственного расхождения двух масок либо -1."""
    pos = -1
    seen = 0
    for idx, (a, b) in enumerate(zip(left, right)):
        if a != b:
            seen += 1
            pos = idx
            if seen > 1:
                return -1
    return pos


def _glue_pass(masks: Iterable[str]) -> tuple[set[str], set[str]]:
    """Один проход склеивания.

    Возвращает (новые_склеенные_маски, маски_не_вошедшие_ни_в_одну_пару).
    Вторые становятся кандидатами в простые импликанты.
    """
    masks = list(dict.fromkeys(masks))  # убираем дубли, сохраняя порядок
    merged: set[str] = set()
    consumed: set[str] = set()
    for a, b in combinations(masks, 2):
        spot = _single_mismatch(a, b)
        if spot != -1:
            glued = a[:spot] + WILDCARD + a[spot + 1:]
            merged.add(glued)
            consumed.add(a)
            consumed.add(b)
    leftovers = {m for m in masks if m not in consumed}
    return merged, leftovers


def prime_implicants(masks: Sequence[str]) -> list[str]:
    """Полный цикл склеивания до стабилизации — возвращает простые импликанты."""
    if not masks:
        return []
    current = list(dict.fromkeys(masks))
    primes: set[str] = set()
    while True:
        merged, leftovers = _glue_pass(current)
        primes |= leftovers
        if not merged:
            primes |= set(current)
            break
        current = list(merged)
    return sorted(primes)


def _matches(mask: str, term: str) -> bool:
    """Проверяет, накрывает ли маска конкретный набор."""
    return all(m == WILDCARD or m == t for m, t in zip(mask, term))


def minimal_cover(primes: Sequence[str], targets: Sequence[str]) -> list[str]:
    """Выбирает минимальный набор импликант, накрывающий все целевые наборы."""
    pending = set(targets)
    if not pending or not primes:
        return []
    picked: list[str] = []

    # Шаг 1: ядровые импликанты — единственные накрывающие данный набор.
    for term in list(pending):
        cover_options = [p for p in primes if _matches(p, term)]
        if len(cover_options) == 1:
            core = cover_options[0]
            if core not in picked:
                picked.append(core)
                pending -= {t for t in pending if _matches(core, t)}

    # Шаг 2: жадно добираем остаток, пока что-то не накрыто.
    while pending:
        best = max(primes, key=lambda p: sum(1 for t in pending if _matches(p, t)))
        picked.append(best)
        pending -= {t for t in pending if _matches(best, t)}

    return picked


def render(masks: Sequence[str], names: Sequence[str], as_dnf: bool) -> str:
    """Собирает символьную запись формулы из набора масок."""
    if not masks:
        return "0" if as_dnf else "1"

    blocks: list[str] = []
    for mask in masks:
        literals: list[str] = []
        for sym, name in zip(mask, names):
            if sym == WILDCARD:
                continue
            # ДНФ: 1 -> прямой, 0 -> инверсный. КНФ: наоборот.
            direct = sym == "1" if as_dnf else sym == "0"
            literals.append(name if direct else f"!{name}")
        if not literals:
            # Маска целиком из wildcard -> терм-константа (тождественная 1/0).
            return "1" if as_dnf else "0"
        joiner = " & " if as_dnf else " | "
        blocks.append("(" + joiner.join(literals) + ")")

    outer = " | " if as_dnf else " & "
    return outer.join(blocks)


def minimize(rows: Sequence[Row], names: Sequence[str], as_dnf: bool = True) -> str:
    """Главная точка входа: таблица -> минимизированная формула (СДНФ/СКНФ)."""
    glue_input = _selected_patterns(rows, want_one=as_dnf, with_dc=True)
    primes = prime_implicants(glue_input)
    targets = _selected_patterns(rows, want_one=as_dnf, with_dc=False)
    cover = minimal_cover(primes, targets)
    return render(cover, names, as_dnf)
