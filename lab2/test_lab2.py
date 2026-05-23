import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.parser import parse
from core.exceptions import ParserError
from logic.truth_table import build_truth_table
from algebra.dnf_cnf import build_sdnf, build_sknf, numeric_forms, index_form
from algebra.fictive_vars import find_fictive_vars
from algebra.zhegalkin import build_zhegalkin, zhegalkin_to_string
from algebra.post_classes import is_T0, is_T1, is_self_dual, is_monotone, is_linear
from algebra.derivatives import partial_derivative, mixed_derivative
from minimization.quine_mccluskey import minimize_dnf, quine_mccluskey, implicant_to_term
from minimization.karnaugh import build_karnaugh_map, minimize_karnaugh
from utils.binary_utils import int_to_bin, count_ones, differs_by_one_bit


class TestParser(unittest.TestCase):
    def test_parse_simple_variable(self):
        ast = parse("a")
        self.assertEqual(ast.get_vars(), {"a"})
        self.assertEqual(ast.evaluate({"a": 1}), 1)

    def test_parse_not(self):
        ast = parse("!a")
        self.assertEqual(ast.get_vars(), {"a"})
        self.assertEqual(ast.evaluate({"a": 0}), 1)
        self.assertEqual(ast.evaluate({"a": 1}), 0)

    def test_parse_and(self):
        ast = parse("a & b")
        self.assertEqual(ast.get_vars(), {"a", "b"})
        self.assertEqual(ast.evaluate({"a": 1, "b": 1}), 1)
        self.assertEqual(ast.evaluate({"a": 1, "b": 0}), 0)

    def test_parse_or(self):
        ast = parse("a | b")
        self.assertEqual(ast.evaluate({"a": 0, "b": 0}), 0)
        self.assertEqual(ast.evaluate({"a": 1, "b": 0}), 1)

    def test_parse_implication(self):
        ast = parse("a -> b")
        self.assertEqual(ast.evaluate({"a": 1, "b": 0}), 0)
        self.assertEqual(ast.evaluate({"a": 1, "b": 1}), 1)

    def test_parse_equivalence(self):
        ast = parse("a ~ b")
        self.assertEqual(ast.evaluate({"a": 1, "b": 1}), 1)
        self.assertEqual(ast.evaluate({"a": 1, "b": 0}), 0)

    def test_parse_complex(self):
        ast = parse("(a & b) | c")
        self.assertEqual(ast.get_vars(), {"a", "b", "c"})
        self.assertEqual(ast.evaluate({"a": 1, "b": 1, "c": 0}), 1)
        self.assertEqual(ast.evaluate({"a": 1, "b": 0, "c": 0}), 0)

    def test_parser_error_invalid_symbol(self):
        with self.assertRaises(ParserError):
            parse("a $ b")

    def test_parser_error_empty(self):
        with self.assertRaises(ParserError):
            parse("")


class TestTruthTable(unittest.TestCase):
    def test_build_truth_table_single_var(self):
        ast = parse("a")
        vars_list, table = build_truth_table(ast)
        self.assertEqual(vars_list, ["a"])
        self.assertEqual(len(table), 2)
        self.assertEqual(table[0][1], 0)
        self.assertEqual(table[1][1], 1)

    def test_build_truth_table_two_vars(self):
        ast = parse("a & b")
        vars_list, table = build_truth_table(ast)
        self.assertEqual(vars_list, ["a", "b"])
        self.assertEqual(table[-1][1], 1)
        self.assertEqual(table[0][1], 0)


class TestDnfCnf(unittest.TestCase):
    def setUp(self):
        self.ast_and = parse("a & b")
        self.vars_and, self.table_and = build_truth_table(self.ast_and)
        self.ast_xor = parse("(a & !b) | (!a & b)")
        self.vars_xor, self.table_xor = build_truth_table(self.ast_xor)

    def test_build_sdnf_and(self):
        sdnf = build_sdnf(self.vars_and, self.table_and)
        self.assertEqual(sdnf, "(a & b)")

    def test_build_sknf_and(self):
        sknf = build_sknf(self.vars_and, self.table_and)
        self.assertIn("(a | b)", sknf)
        self.assertIn("(a | !b)", sknf)
        self.assertIn("(!a | b)", sknf)

    def test_build_sdnf_xor(self):
        sdnf = build_sdnf(self.vars_xor, self.table_xor)
        self.assertIn("(!a & b)", sdnf)
        self.assertIn("(a & !b)", sdnf)

    def test_build_sknf_xor(self):
        sknf = build_sknf(self.vars_xor, self.table_xor)
        self.assertIn("(a | b)", sknf)
        self.assertIn("(!a | !b)", sknf)

    def test_numeric_forms(self):
        ast = parse("a & b")
        _, table = build_truth_table(ast)
        ones, zeros = numeric_forms(table)
        self.assertEqual(ones, [3])
        self.assertEqual(zeros, [0, 1, 2])

    def test_index_form(self):
        ast = parse("a & b")
        _, table = build_truth_table(ast)
        idx = index_form(table)
        self.assertEqual(idx, "0001")


class TestFictiveVars(unittest.TestCase):
    def test_no_fictive(self):
        ast = parse("a & b")
        vars_list, table = build_truth_table(ast)
        fictive = find_fictive_vars(vars_list, table)
        self.assertEqual(fictive, [])

    def test_fictive_var(self):
        ast = parse("a | (b & !b)")
        vars_list, table = build_truth_table(ast)
        fictive = find_fictive_vars(vars_list, table)
        self.assertIn("b", fictive)
        self.assertEqual(len(fictive), 1)


class TestZhegalkin(unittest.TestCase):
    def test_zhegalkin_and(self):
        ast = parse("a & b")
        vars_list, table = build_truth_table(ast)
        coeffs = build_zhegalkin(table)
        self.assertEqual(coeffs, [0, 0, 0, 1])
        poly = zhegalkin_to_string(vars_list, coeffs)
        self.assertEqual(poly, "ab")

    def test_zhegalkin_xor(self):
        ast = parse("(a & !b) | (!a & b)")
        vars_list, table = build_truth_table(ast)
        coeffs = build_zhegalkin(table)
        self.assertEqual(coeffs, [0, 1, 1, 0])
        poly = zhegalkin_to_string(vars_list, coeffs)
        terms = poly.split(" ⊕ ")
        self.assertEqual(set(terms), {"a", "b"})

    def test_zhegalkin_constant_one(self):
        # функция-константа 1 (тавтология)
        ast = parse("a | !a")
        vars_list, table = build_truth_table(ast)
        coeffs = build_zhegalkin(table)
        self.assertEqual(coeffs, [1, 0])
        poly = zhegalkin_to_string(vars_list, coeffs)
        self.assertEqual(poly, "1")


class TestPostClasses(unittest.TestCase):
    def setUp(self):
        self.ast_and = parse("a & b")
        self.vars_and, self.table_and = build_truth_table(self.ast_and)
        self.ast_or = parse("a | b")
        _, self.table_or = build_truth_table(self.ast_or)
        self.ast_not = parse("!a")
        _, self.table_not = build_truth_table(self.ast_not)
        self.ast_xor = parse("(a & !b) | (!a & b)")
        _, self.table_xor = build_truth_table(self.ast_xor)
        self.coeffs_linear = [0, 1, 1, 0]

    def test_T0(self):
        self.assertTrue(is_T0(self.table_and))
        self.assertFalse(is_T0(self.table_not))

    def test_T1(self):
        self.assertTrue(is_T1(self.table_and))
        self.assertFalse(is_T1(self.table_not))

    def test_self_dual(self):
        self.assertFalse(is_self_dual(self.table_xor))
        self.assertTrue(is_self_dual(self.table_not))

    def test_monotone(self):
        self.assertTrue(is_monotone(self.vars_and, self.table_and))
        self.assertFalse(is_monotone(["a", "b"], self.table_xor))

    def test_linear(self):
        self.assertTrue(is_linear(self.coeffs_linear))
        coeffs_nonlinear = [0, 0, 0, 1]
        self.assertFalse(is_linear(coeffs_nonlinear))


class TestDerivatives(unittest.TestCase):
    def test_partial_derivative(self):
        ast = parse("a & b")
        _, table = build_truth_table(ast)
        deriv_a = partial_derivative(ast, table, "a")
        self.assertEqual(deriv_a, [0, 1, 0, 1])
        deriv_b = partial_derivative(ast, table, "b")
        self.assertEqual(deriv_b, [0, 0, 1, 1])

    def test_mixed_derivative(self):
        ast = parse("a & b")
        _, table = build_truth_table(ast)
        mixed = mixed_derivative(ast, table, ["a", "b"])
        self.assertEqual(len(mixed), 4)
        self.assertEqual(mixed, [1, 1, 1, 1])


class TestMinimization(unittest.TestCase):
    def setUp(self):
        self.ast_majority = parse("(a & b) | (a & c) | (b & c)")
        self.vars_maj, self.table_maj = build_truth_table(self.ast_majority)

    def test_quine_mccluskey_majority(self):
        implicants = quine_mccluskey(self.vars_maj, self.table_maj)
        self.assertEqual(len(implicants), 3)
        self.assertIn("11-", implicants)
        self.assertIn("1-1", implicants)
        self.assertIn("-11", implicants)

    def test_minimize_dnf_majority(self):
        dnf = minimize_dnf(self.vars_maj, self.table_maj)
        self.assertIn("a & b", dnf)
        self.assertIn("a & c", dnf)
        self.assertIn("b & c", dnf)

    def test_implicant_to_term(self):
        self.assertEqual(implicant_to_term("10-", ["a", "b", "c"]), "a & !b")
        self.assertEqual(implicant_to_term("111", ["a", "b", "c"]), "a & b & c")
        self.assertEqual(implicant_to_term("---", ["a", "b", "c"]), "1")

    def test_karnaugh_map_building(self):
        ast_and = parse("a & b")
        vars_and, table_and = build_truth_table(ast_and)
        kmap = build_karnaugh_map(vars_and, table_and)
        self.assertEqual(kmap, [[0, 0], [0, 1]])
        kmap3 = build_karnaugh_map(self.vars_maj, self.table_maj)
        self.assertEqual(len(kmap3), 2)
        self.assertEqual(len(kmap3[0]), 4)

    def test_minimize_karnaugh(self):
        dnf = minimize_karnaugh(self.vars_maj, self.table_maj)
        self.assertIn("a & b", dnf)
        self.assertIn("a & c", dnf)
        self.assertIn("b & c", dnf)


class TestBinaryUtils(unittest.TestCase):
    def test_int_to_bin(self):
        self.assertEqual(int_to_bin(5, 3), "101")
        self.assertEqual(int_to_bin(0, 4), "0000")

    def test_count_ones(self):
        self.assertEqual(count_ones(5), 2)
        self.assertEqual(count_ones(0), 0)

    def test_differs_by_one_bit(self):
        self.assertTrue(differs_by_one_bit("101", "111"))
        self.assertFalse(differs_by_one_bit("101", "010"))


if __name__ == "__main__":
    unittest.main()