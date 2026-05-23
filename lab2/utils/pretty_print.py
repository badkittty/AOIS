def print_table(vars_list, table):
    print(" | ".join(vars_list) + " | f")
    print("-" * (4 * len(vars_list) + 5))
    for context, value in table:
        row = [str(context[v]) for v in vars_list]
        print(" | ".join(row) + f" | {value}")

def print_section(title):
    print("\n" + "=" * 50)
    print(title)
    print("=" * 50)