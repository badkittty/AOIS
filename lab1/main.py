from integer_arithmetic import IntegerArithmetic
from float_arithmetic import FloatArithmetic
from bcd_arithmetic import BCDArithmetic
from validators import Validators
from converters import NumberConverter

def input_int(prompt):
    s = input(prompt)
    ok, res = Validators.validate_integer_input(s)
    if not ok:
        print(f"Ошибка: {res}")
        return None
    return res

def main():
    int_arith = IntegerArithmetic()
    float_arith = FloatArithmetic()
    conv = NumberConverter()

    while True:
        print("\n--- Лабораторная работа 1 ---")
        print("1. Перевод целого числа в коды")
        print("2. Сложение целых в дополнительном коде")
        print("3. Вычитание целых в дополнительном коде")
        print("4. Умножение целых в прямом коде")
        print("5. Деление целых в прямом коде")
        print("6. Сложение чисел с плавающей точкой (IEEE-754)")
        print("7. Вычитание чисел с плавающей точкой")
        print("8. Умножение чисел с плавающей точкой")
        print("9. Деление чисел с плавающей точкой")
        print("10. Сложение в коде Excess-3")
        print("0. Выход")
        choice = input("Выберите операцию: ")

        if choice == '0': break
        elif choice == '1':
            num = input_int("Введите целое число: ")
            if num is None: continue
            d = conv.decimal_to_direct(num)
            r = conv.decimal_to_reverse(num)
            a = conv.decimal_to_additional(num)
            print(f"Прямой:       {d.to_string()}")
            print(f"Обратный:     {r.to_string()}")
            print(f"Дополнительный: {a.to_string()}")

        elif choice == '2':
            a = input_int("Первое: "); b = input_int("Второе: ")
            if a is None or b is None: continue
            bits, dec = int_arith.add_additional(a, b)
            print(f"Сумма: {dec}\nБиты: {bits.to_string()}")

        elif choice == '3':
            a = input_int("Уменьшаемое: "); b = input_int("Вычитаемое: ")
            if a is None or b is None: continue
            bits, dec = int_arith.subtract_additional(a, b)
            print(f"Разность: {dec}\nБиты: {bits.to_string()}")

        elif choice == '4':
            a = input_int("Множимое: "); b = input_int("Множитель: ")
            if a is None or b is None: continue
            bits, dec = int_arith.multiply_direct(a, b)
            print(f"Произведение: {dec}\nБиты: {bits.to_string()}")

        elif choice == '5':
            a = input_int("Делимое: "); b = input_int("Делитель: ")
            if a is None or b is None: continue
            try:
                bits, dec = int_arith.divide_direct(a, b)
                print(f"Частное: {dec}\nБиты: {bits.to_string()}")
            except ZeroDivisionError as e:
                print(e)

        elif choice == '6':
            a = float(input("Первое float: ")); b = float(input("Второе float: "))
            bits, dec = float_arith.add_float(a, b)
            print(f"Сумма: {dec}\nБиты: {bits.to_string()}")

        elif choice == '7':
            a = float(input("Уменьшаемое float: ")); b = float(input("Вычитаемое float: "))
            bits, dec = float_arith.subtract_float(a, b)
            print(f"Разность: {dec}\nБиты: {bits.to_string()}")

        elif choice == '8':
            a = float(input("Множимое float: ")); b = float(input("Множитель float: "))
            bits, dec = float_arith.multiply_float(a, b)
            print(f"Произведение: {dec}\nБиты: {bits.to_string()}")

        elif choice == '9':
            a = float(input("Делимое float: ")); b = float(input("Делитель float: "))
            try:
                bits, dec = float_arith.divide_float(a, b)
                print(f"Частное: {dec}\nБиты: {bits.to_string()}")
            except ZeroDivisionError as e:
                print(e)

        elif choice == '10':
            a_str = input("Первое число (только цифры): ")
            b_str = input("Второе число (только цифры): ")
            if not (a_str.isdigit() and b_str.isdigit()):
                print("Ошибка: введите неотрицательные целые.")
                continue
            ok_a, _ = Validators.validate_bcd_length(a_str)
            ok_b, _ = Validators.validate_bcd_length(b_str)
            if not (ok_a and ok_b):
                print("Ошибка: число слишком длинное (макс. 9 цифр).")
                continue
            a_bits = BCDArithmetic.decimal_to_excess3(a_str)
            b_bits = BCDArithmetic.decimal_to_excess3(b_str)
            sum_bits = BCDArithmetic.add_excess3(a_bits, b_bits)
            dec = BCDArithmetic.excess3_to_decimal(sum_bits)
            print(f"Сумма в Excess-3: {''.join(map(str,sum_bits))}")
            print(f"Десятичная сумма: {dec}")

if __name__ == "__main__":
    main()