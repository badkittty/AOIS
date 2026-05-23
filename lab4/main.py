import sys
from hash_table.table import HashTable
from hash_table.data_provider import initial_data
from hash_table.hasher import word_to_value, hash_function

def print_menu():
    print("\n" + "=" * 60)
    print("ХЕШ-ТАБЛИЦА (тематика: Грамматика)")
    print("1. Вывести всю таблицу")
    print("2. Найти запись по ключевому слову")
    print("3. Добавить новую запись")
    print("4. Удалить запись")
    print("5. Показать числовое значение и хеш-адрес для ключа")
    print("6. Коэффициент заполнения")
    print("0. Выход")
    print("=" * 60)

def main():
    table = HashTable()
    print("Инициализация хеш-таблицы...")
    for key, data in initial_data:
        success = table.insert(key, data)
        if not success:
            print(f"Не удалось добавить '{key}'")
    print(f"Загружено записей: {sum(1 for rec in table.table if not rec.is_free())}")
    table.display()

    while True:
        print_menu()
        choice = input("Выберите действие: ").strip()
        if choice == "1":
            table.display()
        elif choice == "2":
            key = input("Введите ключевое слово: ").strip()
            res = table.search(key)
            if res:
                idx, rec = res
                print(f"Найдено в строке {idx}: ID={rec.id}, данные={rec.pi}")
            else:
                print("Запись не найдена.")
        elif choice == "3":
            key = input("Введите новое ключевое слово: ").strip()
            data = input("Введите данные (определение): ").strip()
            if table.insert(key, data):
                print("Запись добавлена.")
            else:
                print("Добавление не удалось.")
        elif choice == "4":
            key = input("Введите ключевое слово для удаления: ").strip()
            if table.delete(key):
                print("Запись удалена.")
            else:
                print("Удаление не удалось.")
        elif choice == "5":
            key = input("Введите ключевое слово: ").strip()
            val = word_to_value(key)
            h = hash_function(val)
            print(f"V = {val}, h = {h}")
        elif choice == "6":
            lf = table.get_load_factor()
            print(f"Коэффициент заполнения: {lf:.2f} ({int(lf*TABLE_SIZE)}/{TABLE_SIZE})")
        elif choice == "0":
            print("До свидания!")
            sys.exit(0)
        else:
            print("Неверный ввод, попробуйте снова.")

if __name__ == "__main__":
    main()