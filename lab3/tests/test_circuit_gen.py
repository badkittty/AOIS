"""Тесты генератора схем Logisim."""

import xml.dom.minidom as minidom

from circuit_gen import _parse_terms, build_circuit


def test_parse_single_term():
    assert _parse_terms("(a & !b)") == [["a", "!b"]]


def test_parse_multiple_terms():
    assert _parse_terms("(a & b) | (c)") == [["a", "b"], ["c"]]


def test_parse_constant():
    assert _parse_terms("1") == [["1"]]
    assert _parse_terms("0") == [["0"]]


def test_build_circuit_is_valid_xml():
    text = build_circuit("Demo", ["a", "b"], {"f": "(a & b) | (!a)"}, as_dnf=True)
    doc = minidom.parseString(text)  # бросит исключение при ошибке разметки
    assert doc.getElementsByTagName("circuit")


def test_build_circuit_constant_output():
    text = build_circuit("C", ["a"], {"f": "1"}, as_dnf=True)
    assert "Constant" in text
    assert '0x1' in text


def test_build_circuit_has_pins():
    text = build_circuit("P", ["a", "b"], {"y": "(a & b)"}, as_dnf=True)
    # Два входных контакта + один выходной.
    assert text.count('name="Pin"') == 3


def test_build_circuit_knf_uses_or_inner():
    text = build_circuit("K", ["a", "b"], {"y": "(a | b)"}, as_dnf=False)
    assert "OR Gate" in text


def test_build_circuit_creates_inverters():
    text = build_circuit("I", ["a"], {"y": "(!a)"}, as_dnf=True)
    assert "NOT Gate" in text
