def find_fictive_vars(variables, table):
    fictive = []
    for var in variables:
        is_fictive = True
        # Словарь для быстрой проверки: для каждого набора значений остальных переменных
        # запомним значение f при var=0 и var=1
        groups = {}
        for context, val in table:
            key = tuple(v for v_name, v in context.items() if v_name != var)
            if key not in groups:
                groups[key] = {}
            groups[key][context[var]] = val
        for key, d in groups.items():
            if 0 in d and 1 in d and d[0] != d[1]:
                is_fictive = False
                break
        if is_fictive:
            fictive.append(var)
    return fictive