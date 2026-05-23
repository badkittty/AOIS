def build_sdnf(variables, table):
    terms = []
    for context, value in table:
        if value == 1:
            literals = []
            for var in variables:
                if context[var] == 1:
                    literals.append(var)
                else:
                    literals.append(f"!{var}")
            terms.append("(" + " & ".join(literals) + ")")
    return " | ".join(terms) if terms else "0"

def build_sknf(variables, table):
    terms = []
    for context, value in table:
        if value == 0:
            literals = []
            for var in variables:
                if context[var] == 0:
                    literals.append(var)
                else:
                    literals.append(f"!{var}")
            terms.append("(" + " | ".join(literals) + ")")
    return " & ".join(terms) if terms else "1"

def numeric_forms(table):
    ones = [i for i, (_, val) in enumerate(table) if val == 1]
    zeros = [i for i, (_, val) in enumerate(table) if val == 0]
    return ones, zeros

def index_form(table):
    bits = ''.join(str(val) for _, val in table)
    return bits