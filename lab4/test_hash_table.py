import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from hash_table.constants import TABLE_SIZE
from hash_table.hasher import letter_to_number, word_to_value, hash_function
from hash_table.record import Record
from hash_table.table import HashTable

# ----------------------------------------------------------------------
# Вспомогательные функции для генерации валидных русских ключей
# ----------------------------------------------------------------------
RUSSIAN_LETTERS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

def make_valid_keys(count: int) -> list:
    """Генерирует count уникальных двухбуквенных русских ключей."""
    keys = []
    for i in range(count):
        first = RUSSIAN_LETTERS[i // len(RUSSIAN_LETTERS)]
        second = RUSSIAN_LETTERS[i % len(RUSSIAN_LETTERS)]
        keys.append(first + second)
    return keys

# ----------------------------------------------------------------------
class TestHasher(unittest.TestCase):
    def test_letter_to_number(self):
        self.assertEqual(letter_to_number('а'), 0)
        self.assertEqual(letter_to_number('я'), 32)
        self.assertEqual(letter_to_number('ё'), 6)
        self.assertEqual(letter_to_number('A'), 0)

    def test_word_to_value(self):
        self.assertEqual(word_to_value("Вяткин"), 2*33 + 32)   # 98
        self.assertEqual(word_to_value("Третьяк"), 19*33 + 17) # 644
        self.assertEqual(word_to_value("А"), 0)
        self.assertEqual(word_to_value(""), 0)
        self.assertEqual(word_to_value("вяткин"), 2*33 + 32)

    def test_hash_function(self):
        self.assertEqual(hash_function(98), 98 % TABLE_SIZE)
        self.assertEqual(hash_function(644), 644 % TABLE_SIZE)

# ----------------------------------------------------------------------
class TestRecord(unittest.TestCase):
    def test_record_init(self):
        r = Record()
        self.assertIsNone(r.id)
        self.assertEqual(r.u, 0)
        self.assertTrue(r.is_free())
        self.assertFalse(r.is_deleted())

    def test_is_free(self):
        r = Record()
        self.assertTrue(r.is_free())
        r.u = 1
        self.assertFalse(r.is_free())

# ----------------------------------------------------------------------
class TestHashTable(unittest.TestCase):
    def setUp(self):
        self.ht = HashTable()

    def test_insert_search(self):
        self.assertTrue(self.ht.insert("Существительное", "часть речи"))
        res = self.ht.search("Существительное")
        self.assertIsNotNone(res)
        idx, rec = res
        self.assertEqual(rec.id, "Существительное")
        self.assertEqual(rec.pi, "часть речи")
        self.assertFalse(self.ht.insert("Существительное", "дубль"))

    def test_collision(self):
        self.ht.insert("Предлог", "служебная")
        self.ht.insert("Приставка", "морфема")
        self.ht.insert("Причастие", "форма")
        self.assertIsNotNone(self.ht.search("Предлог"))
        self.assertIsNotNone(self.ht.search("Приставка"))
        self.assertIsNotNone(self.ht.search("Причастие"))
        idx, rec = self.ht.search("Предлог")
        self.assertEqual(rec.c, 1)

    def test_update(self):
        self.ht.insert("Глагол", "действие")
        self.assertTrue(self.ht.update("Глагол", "новая дефиниция"))
        res = self.ht.search("Глагол")
        self.assertEqual(res[1].pi, "новая дефиниция")
        self.assertFalse(self.ht.update("Нет", "данные"))

    def test_delete(self):
        self.ht.insert("Одиночный", "данные")
        self.assertTrue(self.ht.delete("Одиночный"))
        self.assertIsNone(self.ht.search("Одиночный"))
        self.assertFalse(self.ht.delete("Одиночный"))

    def test_load_factor(self):
        self.assertEqual(self.ht.get_load_factor(), 0.0)
        keys = make_valid_keys(5)
        for i, k in enumerate(keys):
            self.ht.insert(k, f"data{i}")
        self.assertAlmostEqual(self.ht.get_load_factor(), 5 / TABLE_SIZE)

# ----------------------------------------------------------------------
class TestEdgeCases(unittest.TestCase):
    def test_table_full(self):
        ht = HashTable()
        keys = make_valid_keys(TABLE_SIZE)
        for i, k in enumerate(keys):
            self.assertTrue(ht.insert(k, f"d{i}"), f"Failed at {i}")
        self.assertEqual(ht.get_load_factor(), 1.0)
        self.assertFalse(ht.insert("Лишний", "данные"))

    def test_validation(self):
        ht = HashTable()
        self.assertFalse(ht.insert("А", "данные"))      # слишком короткий
        self.assertFalse(ht.insert("Abc", "данные"))    # латиница
        self.assertTrue(ht.insert("Абв", "данные"))

    def test_delete_chain(self):
        ht = HashTable()
        # Используем только русские буквы, без цифр
        ht.insert("Абажур", "1")
        ht.insert("Абакан", "2")
        ht.insert("Абажурр", "3")   # вместо "Абажур2"
        self.assertTrue(ht.delete("Абакан"))
        self.assertIsNotNone(ht.search("Абажур"))
        self.assertIsNotNone(ht.search("Абажурр"))
        self.assertIsNone(ht.search("Абакан"))

    def test_update_deleted(self):
        ht = HashTable()
        ht.insert("Удаляемый", "старые")
        ht.delete("Удаляемый")
        self.assertFalse(ht.update("Удаляемый", "новые"))

# ----------------------------------------------------------------------
if __name__ == "__main__":
    unittest.main()