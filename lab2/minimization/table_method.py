from minimization.quine_mccluskey import quine_mccluskey, implicant_to_term

def table_method(variables, table, dnf=True):
    implicants = quine_mccluskey(variables, table)
    terms = [implicant_to_term(imp, variables) for imp in implicants]
    if dnf:
        return " | ".join(terms) if terms else "0"
    else:
        from algebra.dnf_cnf import build_sknf
        return build_sknf(variables, table)

def print_table_method(variables, table):
    print("Расчетно-табличный метод (Quine-McCluskey)")
    implicants = quine_mccluskey(variables, table)
    print("Простые импликанты:", implicants)
    print("Минимизированная ДНФ:", table_method(variables, table))