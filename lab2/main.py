from core.parser import parse
from logic.truth_table import build_truth_table
from algebra.dnf_cnf import build_sdnf, build_sknf, numeric_forms, index_form
from algebra.post_classes import is_T0, is_T1, is_self_dual, is_monotone, is_linear
from algebra.fictive_vars import find_fictive_vars
from algebra.zhegalkin import build_zhegalkin, zhegalkin_to_string
from algebra.derivatives import partial_derivative, mixed_derivative
from minimization.quine_mccluskey import minimize_dnf
from minimization.table_method import table_method
from minimization.karnaugh import build_karnaugh_map, minimize_karnaugh
from utils.pretty_print import print_table, print_section
from core.exceptions import ParserError

class Application:
    def run(self) -> None:
        expression = input("Введите логическую функцию: ").strip()
        try:
            ast = parse(expression)
        except ParserError as error:
            print(f"Ошибка: {error}")
            return

        variables, table = build_truth_table(ast)

        self._print_truth_table(variables, table)
        self._print_normal_forms(variables, table)
        self._print_numeric_forms(table)
        self._print_index_form(table)
        self._print_fictive_variables(variables, table)
        self._print_zhegalkin(variables, table)
        self._print_post_classes(variables, table)
        self._print_derivatives(ast, variables, table)
        self._print_minimization(variables, table)
        self._print_karnaugh(variables, table)

    @staticmethod
    def _print_truth_table(variables, table):
        print_section("ТАБЛИЦА ИСТИННОСТИ")
        print_table(variables, table)

    @staticmethod
    def _print_normal_forms(variables, table):
        print_section("СДНФ")
        print(build_sdnf(variables, table))
        print_section("СКНФ")
        print(build_sknf(variables, table))

    @staticmethod
    def _print_numeric_forms(table):
        ones, zeros = numeric_forms(table)
        print_section("ЧИСЛОВЫЕ ФОРМЫ")
        print("Σ (наборы, где f=1):", ones)
        print("Π (наборы, где f=0):", zeros)

    @staticmethod
    def _print_index_form(table):
        print_section("ИНДЕКСНАЯ ФОРМА")
        print(index_form(table))

    @staticmethod
    def _print_fictive_variables(variables, table):
        print_section("ФИКТИВНЫЕ ПЕРЕМЕННЫЕ")
        fictive = find_fictive_vars(variables, table)
        print(fictive if fictive else "нет")

    @staticmethod
    def _print_zhegalkin(variables, table):
        print_section("ПОЛИНОМ ЖЕГАЛКИНА")
        coeffs = build_zhegalkin(table)
        poly = zhegalkin_to_string(variables, coeffs)
        print(poly)

    @staticmethod
    def _print_post_classes(variables, table):
        print_section("КЛАССЫ ПОСТА")
        coeffs = build_zhegalkin(table)  # для проверки линейности
        print(f"T0 (сохраняет 0): {is_T0(table)}")
        print(f"T1 (сохраняет 1): {is_T1(table)}")
        print(f"Самодвойственная: {is_self_dual(table)}")
        print(f"Монотонная: {is_monotone(variables, table)}")
        print(f"Линейная: {is_linear(coeffs)}")

    @staticmethod
    def _print_derivatives(ast, variables, table):
        print_section("БУЛЕВЫ ПРОИЗВОДНЫЕ")
        for var in variables:
            deriv = partial_derivative(ast, table, var)
            print(f"∂f/∂{var} = {deriv}")
        # Смешанные производные (для 2,3,4 переменных по желанию)
        if len(variables) >= 2:
            dvars = variables[:2]
            mixed = mixed_derivative(ast, table, dvars)
            print(f"∂²f/∂{dvars[0]}∂{dvars[1]} = {mixed}")

    @staticmethod
    def _print_minimization(variables, table):
        print_section("МИНИМИЗАЦИЯ (расчётный метод Квайна-МакКласки)")
        minimized = minimize_dnf(variables, table)
        print("Минимизированная ДНФ:", minimized)
        print("\nРасчетно-табличный метод:")
        print(table_method(variables, table))

    @staticmethod
    def _print_karnaugh(variables, table):
        print_section("КАРТА КАРНО")
        k_map = build_karnaugh_map(variables, table)
        if isinstance(k_map, list):
            for row in k_map:
                print(row)
        else:
            print(k_map)
        minimized = minimize_karnaugh(variables, table)
        print("Минимизированная ДНФ по карте Карно:", minimized)

if __name__ == "__main__":
    Application().run()