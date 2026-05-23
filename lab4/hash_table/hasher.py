from .constants import ALPHABET_BASE, TABLE_SIZE

# Полный русский алфавит из 33 букв (порядок важен)
RUSSIAN_ALPHABET = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"

def letter_to_number(letter: str) -> int:
    letter = letter.lower()
    if letter in RUSSIAN_ALPHABET:
        return RUSSIAN_ALPHABET.index(letter)
    return 0

def word_to_value(word: str) -> int:
    word = word.lower().strip()
    if len(word) < 2:
        return 0
    first = letter_to_number(word[0])
    second = letter_to_number(word[1])
    return first * ALPHABET_BASE + second

def hash_function(value: int) -> int:
    return value % TABLE_SIZE