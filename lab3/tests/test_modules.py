"""Тесты прикладных модулей: сумматор, Gray BCD, счётчик."""

import pytest

from logic import adder3, counter, gray_bcd


def _eval(formula, names, args):
    if formula in ("0", "1"):
        return int(formula)
    env = dict(zip(names, args))
    expr = formula.replace("!", "not ").replace("&", "and").replace("|", "or")
    return int(bool(eval(expr, {}, env)))


def _formula_matches_table(formula, names, rows):
    for r in rows:
        if r.out is None:
            continue
        if _eval(formula, names, r.args) != r.out:
            return False
    return True


# ----- Часть 1: сумматор -----

def test_sum_sknf_correct():
    assert _formula_matches_table(adder3.sum_sknf(), adder3.INPUT_NAMES, adder3.sum_table())


def test_carry_sknf_correct():
    assert _formula_matches_table(adder3.carry_sknf(), adder3.INPUT_NAMES, adder3.carry_table())


@pytest.mark.parametrize("x,y", [(8, 6), (255, 1), (0, 0), (200, 100), (127, 128)])
def test_add_byte_matches_python(x, y):
    res, carry = adder3.add_byte(x, y)
    assert res == (x + y) & 0xFF
    assert carry == ((x + y) >> 8) & 1


def test_add_byte_demo_eight_plus_six():
    assert adder3.add_byte(8, 6) == (14, 0)


def test_add_byte_rejects_out_of_range():
    with pytest.raises(ValueError):
        adder3.add_byte(256, 0)
    with pytest.raises(ValueError):
        adder3.add_byte(0, -1)


def test_adder_describe_contains_formulas():
    text = adder3.describe()
    assert "СКНФ" in text
    assert "8 + 6 = 14" in text


# ----- Часть 2: Gray BCD -----

def test_gray_bcd_all_outputs_correct():
    forms = gray_bcd.all_formulas()
    for name, formula in forms.items():
        rows = gray_bcd.output_table(name)
        assert _formula_matches_table(formula, gray_bcd.INPUT_NAMES, rows)


def test_gray_bcd_carry_only_on_nine():
    # Перенос (9 -> 10) должен возникать ровно на цифре 9.
    rows = gray_bcd.output_table("carry")
    ones = [r for r in rows if r.out == 1]
    assert len(ones) == 1
    assert ones[0].args == gray_bcd.GRAY_BCD[9]


def test_gray_bcd_invalid_codes_are_dont_care():
    rows = gray_bcd.output_table("y0")
    dc = [r for r in rows if r.out is None]
    # 16 кодов минус 10 валидных = 6 безразличных наборов.
    assert len(dc) == 6


def test_gray_bcd_transform_none_for_invalid():
    # (1,0,0,0) не входит в Gray BCD -> None.
    assert gray_bcd._transform((1, 0, 0, 0)) is None


def test_gray_bcd_describe():
    assert "Gray BCD" in gray_bcd.describe()


# ----- Автомат: счётчик -----

def test_counter_trigger_formulas_correct():
    forms = counter.trigger_formulas()
    for i, name in enumerate(counter.TRIGGERS):
        rows = counter.trigger_table(i)
        assert _formula_matches_table(forms[name], counter.STATE_NAMES, rows)


def test_counter_t0_is_constant_one():
    assert counter.trigger_formulas()["T0"] == "1"


def test_counter_full_cycle():
    seq = counter.transition_sequence()
    assert seq == [0, 1, 2, 3, 4, 5, 6, 7, 0]


def test_counter_t_values_reconstruct_increment():
    # Применяя T_i к текущему состоянию, должны получить (state+1) mod 8.
    for state in range(8):
        nxt = 0
        for i in range(3):
            cur_bit = (state >> (2 - i)) & 1
            t = counter._trigger_value(state, i)
            new_bit = cur_bit ^ t
            nxt |= new_bit << (2 - i)
        assert nxt == (state + 1) % 8


def test_counter_describe():
    assert "счётчик" in counter.describe().lower()
