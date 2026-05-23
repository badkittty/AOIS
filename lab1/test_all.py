import unittest
from bit_array import BitArray
from bit_operations import BitOperations
from converters import NumberConverter
from integer_arithmetic import IntegerArithmetic
from float_arithmetic import FloatArithmetic
from bcd_arithmetic import BCDArithmetic
from validators import Validators


class TestBitArray(unittest.TestCase):
    def test_default_initialization(self):
        ba = BitArray()
        self.assertEqual(len(ba.bits), 32)
        self.assertTrue(all(b == 0 for b in ba.bits))

    def test_custom_bits(self):
        bits = [1] + [0] * 31
        ba = BitArray(bits)
        self.assertEqual(ba.bits, bits)

    def test_to_string_formatting(self):
        ba = BitArray([0] * 32)
        self.assertEqual(ba.to_string(), "00000000 00000000 00000000 00000000")
        ba.bits[0] = 1
        self.assertEqual(ba.to_string(), "10000000 00000000 00000000 00000000")


class TestBitOperations(unittest.TestCase):
    def test_add_bits_no_carry(self):
        a = [0] * 32
        b = [0] * 32
        a[31] = 1
        b[31] = 1
        res, carry = BitOperations.add_bits(a, b)
        self.assertEqual(carry, 0)
        self.assertEqual(res[30], 1)
        self.assertEqual(res[31], 0)

    def test_add_bits_with_carry_out(self):
        a = [1] * 32
        b = [1] * 32
        res, carry = BitOperations.add_bits(a, b)
        self.assertEqual(carry, 1)

    def test_invert_bits(self):
        bits = [0] * 32
        bits[0] = 1
        inv = BitOperations.invert_bits(bits)
        self.assertEqual(inv[0], 0)
        self.assertEqual(inv[31], 1)

    def test_shift_left(self):
        bits = [0] * 32
        bits[31] = 1
        shifted = BitOperations.shift_left(bits, fill=0)
        self.assertEqual(shifted[30], 1)
        self.assertEqual(shifted[31], 0)

    def test_compare_registers(self):
        a = [0, 1, 0]
        b = [0, 1, 0]
        self.assertEqual(BitOperations.compare_registers(a, b), 0)
        b[2] = 1  # b = [0,1,1]
        self.assertEqual(BitOperations.compare_registers(a, b), -1)  # a < b
        a = [0, 1, 1]  # теперь a > b
        b = [0, 1, 0]
        self.assertEqual(BitOperations.compare_registers(a, b), 1)

    def test_sub_register(self):
        a = [0, 0, 1]  # 1
        b = [0, 0, 0]  # 0
        res = BitOperations.sub_register(a, b)
        self.assertEqual(res, a)
        a = [0, 1, 0]  # 2
        b = [0, 0, 1]  # 1
        res = BitOperations.sub_register(a, b)
        self.assertEqual(res, [0, 0, 1])


class TestNumberConverter(unittest.TestCase):
    def setUp(self):
        self.conv = NumberConverter()

    def test_direct_code_positive(self):
        ba = self.conv.decimal_to_direct(5)
        self.assertEqual(ba.bits[0], 0)
        self.assertEqual(self.conv.direct_to_decimal(ba), 5)

    def test_direct_code_negative(self):
        ba = self.conv.decimal_to_direct(-5)
        self.assertEqual(ba.bits[0], 1)
        self.assertEqual(self.conv.direct_to_decimal(ba), -5)

    def test_direct_code_zero(self):
        ba = self.conv.decimal_to_direct(0)
        self.assertEqual(ba.bits[0], 0)
        self.assertEqual(self.conv.direct_to_decimal(ba), 0)

    def test_reverse_code_positive(self):
        ba = self.conv.decimal_to_reverse(5)
        self.assertEqual(ba.bits, self.conv.decimal_to_direct(5).bits)

    def test_reverse_code_negative(self):
        ba = self.conv.decimal_to_reverse(-5)
        self.assertEqual(ba.bits[0], 1)
        direct_neg = self.conv.decimal_to_direct(-5).bits
        self.assertNotEqual(ba.bits, direct_neg)

    def test_additional_code_positive(self):
        ba = self.conv.decimal_to_additional(5)
        self.assertEqual(ba.bits[0], 0)
        self.assertEqual(self.conv.additional_to_decimal(ba), 5)

    def test_additional_code_negative(self):
        ba = self.conv.decimal_to_additional(-5)
        self.assertEqual(ba.bits[0], 1)
        self.assertEqual(self.conv.additional_to_decimal(ba), -5)

    def test_additional_code_min_int(self):
        min_int = -2147483648
        ba = self.conv.decimal_to_additional(min_int)
        expected = [1] + [0] * 31
        self.assertEqual(ba.bits, expected)
        self.assertEqual(self.conv.additional_to_decimal(ba), min_int)

    def test_fixed_point_conversion(self):
        value = 12.75
        ba = self.conv.decimal_to_fixed(value)
        dec = self.conv.fixed_to_decimal(ba)
        self.assertAlmostEqual(dec, value, places=5)

        value_neg = -3.5
        ba = self.conv.decimal_to_fixed(value_neg)
        dec = self.conv.fixed_to_decimal(ba)
        self.assertAlmostEqual(dec, value_neg, places=5)

    def test_float_to_ieee754_positive(self):
        ba = self.conv.float_to_ieee754(5.25)
        dec = self.conv.ieee754_to_float(ba)
        self.assertAlmostEqual(dec, 5.25, places=5)

    def test_float_to_ieee754_negative(self):
        ba = self.conv.float_to_ieee754(-0.75)
        dec = self.conv.ieee754_to_float(ba)
        self.assertAlmostEqual(dec, -0.75, places=5)

    def test_float_zero(self):
        ba = self.conv.float_to_ieee754(0.0)
        self.assertTrue(all(b == 0 for b in ba.bits))
        self.assertEqual(self.conv.ieee754_to_float(ba), 0.0)

    def test_float_infinity(self):
        inf_bits = BitArray([0, 1, 1, 1, 1, 1, 1, 1, 1] + [0] * 23)
        dec = self.conv.ieee754_to_float(inf_bits)
        self.assertEqual(dec, float('inf'))

    def test_float_nan(self):
        nan_bits = BitArray([0, 1, 1, 1, 1, 1, 1, 1, 1] + [1] * 23)
        dec = self.conv.ieee754_to_float(nan_bits)
        self.assertTrue(dec != dec)


class TestIntegerArithmetic(unittest.TestCase):
    def setUp(self):
        self.arith = IntegerArithmetic()

    def test_add_additional_positive(self):
        bits, dec = self.arith.add_additional(10, 20)
        self.assertEqual(dec, 30)

    def test_add_additional_negative_positive(self):
        bits, dec = self.arith.add_additional(-10, 20)
        self.assertEqual(dec, 10)

    def test_add_additional_both_negative(self):
        bits, dec = self.arith.add_additional(-5, -7)
        self.assertEqual(dec, -12)

    def test_add_additional_overflow(self):
        bits, dec = self.arith.add_additional(2000000000, 2000000000)
        self.assertNotEqual(dec, 4000000000)

    def test_subtract_additional(self):
        bits, dec = self.arith.subtract_additional(10, 20)
        self.assertEqual(dec, -10)

    def test_negate_additional(self):
        self.assertEqual(self.arith.negate_additional(5), -5)
        self.assertEqual(self.arith.negate_additional(-5), 5)
        self.assertEqual(self.arith.negate_additional(0), 0)
        self.assertEqual(self.arith.negate_additional(-2147483648), -2147483648)

    def test_multiply_direct_positive(self):
        bits, dec = self.arith.multiply_direct(7, 8)
        self.assertEqual(dec, 56)

    def test_multiply_direct_mixed_signs(self):
        bits, dec = self.arith.multiply_direct(-7, 8)
        self.assertEqual(dec, -56)
        bits, dec = self.arith.multiply_direct(7, -8)
        self.assertEqual(dec, -56)
        bits, dec = self.arith.multiply_direct(-7, -8)
        self.assertEqual(dec, 56)

    def test_multiply_direct_zero(self):
        bits, dec = self.arith.multiply_direct(0, 123)
        self.assertEqual(dec, 0)

    def test_divide_direct_positive(self):
        bits, dec = self.arith.divide_direct(15, 4)
        self.assertAlmostEqual(dec, 3.75, places=5)

    def test_divide_direct_negative(self):
        bits, dec = self.arith.divide_direct(-15, 4)
        self.assertAlmostEqual(dec, -3.75, places=5)

    def test_divide_direct_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            self.arith.divide_direct(10, 0)


class TestFloatArithmetic(unittest.TestCase):
    def setUp(self):
        self.arith = FloatArithmetic()

    def test_add_float_basic(self):
        bits, dec = self.arith.add_float(2.5, 3.75)
        self.assertAlmostEqual(dec, 6.25, places=5)

    def test_add_float_negative(self):
        bits, dec = self.arith.add_float(-2.5, 3.75)
        self.assertAlmostEqual(dec, 1.25, places=5)

    def test_add_float_zero(self):
        bits, dec = self.arith.add_float(0.0, 5.5)
        self.assertAlmostEqual(dec, 5.5, places=5)
        bits, dec = self.arith.add_float(5.5, 0.0)
        self.assertAlmostEqual(dec, 5.5, places=5)

    def test_subtract_float(self):
        bits, dec = self.arith.subtract_float(10.0, 3.25)
        self.assertAlmostEqual(dec, 6.75, places=5)

    def test_multiply_float(self):
        bits, dec = self.arith.multiply_float(2.5, 4.0)
        self.assertAlmostEqual(dec, 10.0, places=5)

    def test_multiply_float_by_zero(self):
        bits, dec = self.arith.multiply_float(0.0, 5.0)
        self.assertEqual(dec, 0.0)

    def test_divide_float(self):
        bits, dec = self.arith.divide_float(7.5, 2.5)
        self.assertAlmostEqual(dec, 3.0, places=5)

    def test_divide_float_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            self.arith.divide_float(1.0, 0.0)

    def test_float_overflow_to_infinity(self):
        large = 1e38
        bits, dec = self.arith.multiply_float(large, large)
        self.assertEqual(dec, float('inf'))

    def test_add_overflow_to_infinity(self):
        a = 3.4e38
        b = 3.4e38
        bits, dec = self.arith.add_float(a, b)
        self.assertEqual(dec, float('inf'))

    def test_add_large_negative_overflow(self):
        a = -3.4e38
        b = -3.4e38
        bits, dec = self.arith.add_float(a, b)
        self.assertEqual(dec, float('-inf'))

    def test_multiply_overflow_to_infinity(self):
        a = 2e38
        b = 2e38
        bits, dec = self.arith.multiply_float(a, b)
        self.assertEqual(dec, float('inf'))

    def test_multiply_negative_overflow(self):
        a = -2e38
        b = 2e38
        bits, dec = self.arith.multiply_float(a, b)
        self.assertEqual(dec, float('-inf'))

    def test_divide_overflow_to_infinity(self):
        a = 1e38
        b = 1e-38
        bits, dec = self.arith.divide_float(a, b)
        self.assertEqual(dec, float('inf'))

    def test_divide_underflow_to_zero(self):
        a = 1e-38
        b = 1e38
        bits, dec = self.arith.divide_float(a, b)
        self.assertEqual(dec, 0.0)

    # Новые тесты для покрытия оставшихся строк
    def test_add_float_same_sign_carry(self):
        a = 1.5
        b = 1.5
        bits, dec = self.arith.add_float(a, b)
        self.assertAlmostEqual(dec, 3.0, places=5)

    def test_multiply_float_rounding(self):
        a = 1.0000001
        b = 1.0000001
        bits, dec = self.arith.multiply_float(a, b)
        self.assertAlmostEqual(dec, a * b, places=6)

    def test_divide_float_normalization(self):
        a = 1.0
        b = 2.0
        bits, dec = self.arith.divide_float(a, b)
        self.assertAlmostEqual(dec, 0.5, places=5)

    def test_divide_float_rounding_up(self):
        a = 1.0
        b = 3.0
        bits, dec = self.arith.divide_float(a, b)
        self.assertAlmostEqual(dec, 1/3, places=6)

    def test_add_float_one_zero(self):
        a = 0.0
        b = 42.0
        bits, dec = self.arith.add_float(a, b)
        self.assertEqual(dec, 42.0)

    def test_multiply_float_one_zero(self):
        a = 0.0
        b = 42.0
        bits, dec = self.arith.multiply_float(a, b)
        self.assertEqual(dec, 0.0)

    def test_divide_float_zero_dividend(self):
        a = 0.0
        b = 5.0
        bits, dec = self.arith.divide_float(a, b)
        self.assertEqual(dec, 0.0)

    def test_excess3_to_decimal(self):
        bits = [1, 0, 0, 0]
        dec = BCDArithmetic.excess3_to_decimal(bits)
        self.assertEqual(dec, 5)

    def test_add_excess3_small(self):
        a = BCDArithmetic.decimal_to_excess3('12')
        b = BCDArithmetic.decimal_to_excess3('34')
        res_bits = BCDArithmetic.add_excess3(a, b)
        dec = BCDArithmetic.excess3_to_decimal(res_bits)
        self.assertEqual(dec, 46)

    def test_add_excess3_with_carry(self):
        a = BCDArithmetic.decimal_to_excess3('99')
        b = BCDArithmetic.decimal_to_excess3('1')
        res_bits = BCDArithmetic.add_excess3(a, b)
        dec = BCDArithmetic.excess3_to_decimal(res_bits)
        self.assertEqual(dec, 100)

    def test_add_excess3_different_lengths(self):
        a = BCDArithmetic.decimal_to_excess3('123')
        b = BCDArithmetic.decimal_to_excess3('45')
        res_bits = BCDArithmetic.add_excess3(a, b)
        dec = BCDArithmetic.excess3_to_decimal(res_bits)
        self.assertEqual(dec, 168)

    def test_add_excess3_large_numbers(self):
        a = BCDArithmetic.decimal_to_excess3('987654')
        b = BCDArithmetic.decimal_to_excess3('123456')
        res_bits = BCDArithmetic.add_excess3(a, b)
        dec = BCDArithmetic.excess3_to_decimal(res_bits)
        self.assertEqual(dec, 1111110)


class TestValidators(unittest.TestCase):
    def test_is_valid_int(self):
        self.assertTrue(Validators.is_valid_int('123'))
        self.assertTrue(Validators.is_valid_int('-456'))
        self.assertFalse(Validators.is_valid_int('12.3'))
        self.assertFalse(Validators.is_valid_int('abc'))

    def test_is_valid_float(self):
        self.assertTrue(Validators.is_valid_float('1.23'))
        self.assertTrue(Validators.is_valid_float('-4.56'))
        self.assertTrue(Validators.is_valid_float('1e-5'))
        self.assertFalse(Validators.is_valid_float('xyz'))

    def test_validate_integer_input(self):
        ok, val = Validators.validate_integer_input('123')
        self.assertTrue(ok)
        self.assertEqual(val, 123)
        ok, msg = Validators.validate_integer_input('3000000000')
        self.assertFalse(ok)
        self.assertIn('диапазон', msg.lower() if msg else '')
        ok, msg = Validators.validate_integer_input('12345678901')
        self.assertFalse(ok)
        self.assertIn('длинное', msg.lower() if msg else '')

    def test_validate_bcd_length(self):
        ok, _ = Validators.validate_bcd_length('123456789')
        self.assertTrue(ok)
        ok, msg = Validators.validate_bcd_length('1234567890')
        self.assertFalse(ok)
        self.assertIn('9', msg)




if __name__ == '__main__':
    unittest.main()