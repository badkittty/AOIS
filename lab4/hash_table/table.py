from typing import Optional, List, Tuple
from .constants import TABLE_SIZE
from .record import Record
from .hasher import word_to_value, hash_function, RUSSIAN_ALPHABET

class HashTable:
    def __init__(self):
        self.table: List[Record] = [Record() for _ in range(TABLE_SIZE)]

    def validate_key(self, key: str) -> bool:
        if len(key) < 2:
            print(f"Длина ключа '{key}' должна быть не менее 2 символов.")
            return False
        for ch in key:
            if ch.lower() not in RUSSIAN_ALPHABET:
                print(f"Недопустимый символ '{ch}' в ключе. Только русские буквы.")
                return False
        return True

    def _find_free_slot(self) -> Optional[int]:
        for i in range(TABLE_SIZE):
            if self.table[i].is_free():
                return i
        return None

    def _search_chain(self, key: str, start_idx: int) -> Optional[int]:
        idx = start_idx
        while idx is not None:
            rec = self.table[idx]
            if rec.u == 1 and not rec.is_deleted() and rec.id == key:
                return idx
            nxt = rec.po
            if nxt is not None and 0 <= nxt < TABLE_SIZE:
                idx = nxt
            else:
                break
        return None

    def _get_chain_last(self, start_idx: int) -> int:
        idx = start_idx
        while True:
            nxt = self.table[idx].po
            if nxt is None:
                return idx
            if nxt == idx:
                return idx
            idx = nxt

    def insert(self, key: str, data: any) -> bool:
        if not self.validate_key(key):
            return False
        if self.search(key) is not None:
            print(f"Ошибка: ключ '{key}' уже существует в таблице.")
            return False

        value = word_to_value(key)
        h = hash_function(value)

        if self.table[h].is_free():
            self._set_record(h, key, data)
            self.table[h].t = 1
            self.table[h].po = None
            return True
        else:
            free_idx = self._find_free_slot()
            if free_idx is None:
                print("Таблица заполнена, вставка невозможна.")
                return False

            self._set_record(free_idx, key, data)
            self.table[free_idx].t = 1
            self.table[free_idx].po = None

            last = self._get_chain_last(h)
            self.table[last].t = 0
            self.table[last].po = free_idx
            self.table[h].c = 1
            return True

    def _set_record(self, idx: int, key: str, data: any):
        rec = self.table[idx]
        rec.id = key
        rec.u = 1
        rec.d = 0
        rec.c = 0
        rec.l = 0
        rec.pi = data

    def search(self, key: str) -> Optional[Tuple[int, Record]]:
        if not self.validate_key(key):
            return None
        value = word_to_value(key)
        h = hash_function(value)
        idx = self._search_chain(key, h)
        if idx is not None:
            return idx, self.table[idx]
        return None

    def update(self, key: str, new_data: any) -> bool:
        res = self.search(key)
        if res:
            idx, _ = res
            self.table[idx].pi = new_data
            return True
        print(f"Ключ '{key}' не найден для обновления.")
        return False

    def delete(self, key: str) -> bool:
        if not self.validate_key(key):
            return False
        value = word_to_value(key)
        h = hash_function(value)
        del_idx = self._search_chain(key, h)
        if del_idx is None:
            print(f"Ключ '{key}' не найден.")
            return False

        rec = self.table[del_idx]
        rec.d = 1

        # Поиск предыдущего элемента в цепочке
        prev_idx = None
        idx = h
        while idx is not None:
            nxt = self.table[idx].po
            if nxt == del_idx:
                prev_idx = idx
                break
            idx = nxt

        # Одиночная запись
        if rec.t == 1 and rec.po is None:
            self.table[del_idx] = Record()
            return True

        # Последняя в цепочке
        if rec.t == 1:
            if prev_idx is not None:
                self.table[prev_idx].t = 1
                self.table[prev_idx].po = None
            self.table[del_idx] = Record()
            return True

        # Не последняя – копируем следующую запись на место удаляемой
        next_idx = rec.po
        if next_idx is not None and 0 <= next_idx < TABLE_SIZE:
            next_rec = self.table[next_idx]
            self.table[del_idx] = next_rec
            self.table[next_idx] = Record()
            if prev_idx is not None:
                self.table[prev_idx].po = del_idx
        else:
            self.table[del_idx] = Record()
        return True

    def get_load_factor(self) -> float:
        occupied = sum(1 for rec in self.table if not rec.is_free())
        return occupied / TABLE_SIZE

    def display(self):
        print("\n" + "=" * 100)
        print(f"{'№':<3} {'ID':<15} {'C':<2} {'U':<2} {'T':<2} {'L':<2} {'D':<2} {'Po':<4} {'Pi (данные)':<40}")
        print("-" * 100)
        for i, rec in enumerate(self.table):
            if rec.is_free():
                print(f"{i:<3} {'':<15} {rec.c:<2} {rec.u:<2} {rec.t:<2} {rec.l:<2} {rec.d:<2} {str(rec.po):<4} {'свободно':<40}")
            else:
                pi_str = str(rec.pi) if rec.pi else ""
                print(f"{i:<3} {str(rec.id):<15} {rec.c:<2} {rec.u:<2} {rec.t:<2} {rec.l:<2} {rec.d:<2} {str(rec.po):<4} {pi_str:<40}")
        print("=" * 100)