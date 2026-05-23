class Validators:
    @staticmethod
    def is_valid_int(s):
        try: int(s); return True
        except: return False

    @staticmethod
    def is_valid_float(s):
        try: float(s); return True
        except: return False

    @staticmethod
    def validate_integer_input(s):
        if not Validators.is_valid_int(s):
            return False, "Введите целое число."
        if len(s.lstrip('-')) > 10:
            return False, "Слишком длинное число."
        value = int(s)
        if value < -2147483648 or value > 2147483647:
            return False, "Число вне 32-битного диапазона."
        return True, value

    @staticmethod
    def validate_bcd_length(s):
        if len(s) > 9:
            return False, "Максимальная длина 9 цифр (ограничение 32 бита)."
        return True, s