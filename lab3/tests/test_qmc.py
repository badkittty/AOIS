"""Тесты ядра минимизации (Квайн — Мак-Класки)."""

import pytest

from logic.qmc import (
    Row,
    build_rows,
    minimal_cover,
    minimize,
    prime_implicants,
    render,
    _matches,
    _single_mismatch,
    _glue_pass,
    _selected_patterns,
)


def _eval_formula(formula: str, names, args) -> int:
    """Вычисляет символьную формулу на конкретном наборе аргументов."""
    if formula in ("0", "1"):
        return int(formula)
    env = dict(zip(names, args))
    expr = formula.replace("!", "not ").replace("&", "and").replace("|", "or")
    return int(bool(eval(expr, {}, env)))


def _truth_equivalent(formula: str, rows, names) -> bool:
    for r in rows:
        if r.out is None:
            continue
        if _eval_formula(formula, names, r.args) != r.out:
            return False
    return True


def test_build_rows_count_and_order():
    rows = build_rows(2, lambda b: b[0] & b[1])
    assert len(rows) == 4
    assert rows[0].args == (0, 0)
    assert rows[-1].args == (1, 1)
    assert rows[-1].out == 1


def test_row_pattern():
    assert Row((1, 0, 1), 1).pattern == "101"


def test_single_mismatch_one_diff():
    assert _single_mismatch("100", "110") == 1


def test_single_mismatch_none():
    assert _single_mismatch("100", "100") == -1


def test_single_mismatch_two_diffs():
    assert _single_mismatch("100", "111") == -1


def test_matches_wildcard():
    assert _matches("1-0", "110")
    assert _matches("1-0", "100")
    assert not _matches("1-0", "101")


def test_glue_pass_merges_pair():
    merged, leftovers = _glue_pass(["00", "01"])
    assert "0-" in merged
    assert leftovers == set()


def test_glue_pass_leftover():
    merged, leftovers = _glue_pass(["00", "11"])
    assert merged == set()
    assert leftovers == {"00", "11"}


def test_prime_implicants_empty():
    assert prime_implicants([]) == []


def test_prime_implicants_full_collapse():
    # Все четыре набора двух переменных -> одна импликанта "--".
    assert prime_implicants(["00", "01", "10", "11"]) == ["--"]


def test_minimal_cover_empty():
    assert minimal_cover([], ["10"]) == []
    assert minimal_cover(["1-"], []) == []


def test_minimal_cover_core_selection():
    primes = ["0-", "-1"]
    targets = ["00", "01", "11"]
    cover = minimal_cover(primes, targets)
    # Оба простых импликанта необходимы для полного покрытия.
    assert set(cover) == {"0-", "-1"}


def test_render_constant_dnf():
    assert render(["--"], ("a", "b"), as_dnf=True) == "1"


def test_render_constant_knf():
    assert render(["--"], ("a", "b"), as_dnf=False) == "0"


def test_render_empty():
    assert render([], ("a",), as_dnf=True) == "0"
    assert render([], ("a",), as_dnf=False) == "1"


def test_selected_patterns_dc():
    rows = [Row((0,), 1), Row((1,), None)]
    assert _selected_patterns(rows, want_one=True, with_dc=True) == ["0", "1"]
    assert _selected_patterns(rows, want_one=True, with_dc=False) == ["0"]


def test_minimize_dnf_xor():
    # XOR двух переменных не минимизируется и остаётся в полной СДНФ.
    rows = build_rows(2, lambda b: b[0] ^ b[1])
    f = minimize(rows, ("a", "b"), as_dnf=True)
    assert _truth_equivalent(f, rows, ("a", "b"))


def test_minimize_knf_equivalence():
    rows = build_rows(3, lambda b: 1 if sum(b) >= 2 else 0)
    f = minimize(rows, ("a", "b", "c"), as_dnf=False)
    assert _truth_equivalent(f, rows, ("a", "b", "c"))


def test_minimize_all_ones_is_constant():
    rows = build_rows(2, lambda b: 1)
    assert minimize(rows, ("a", "b"), as_dnf=True) == "1"


def test_minimize_all_zeros_dnf():
    rows = build_rows(2, lambda b: 0)
    assert minimize(rows, ("a", "b"), as_dnf=True) == "0"
