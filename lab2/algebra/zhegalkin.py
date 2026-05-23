def build_zhegalkin(table):
    values = [v for _, v in table]
    triangle = [values]
    while len(triangle[-1]) > 1:
        prev = triangle[-1]
        next_row = [prev[i] ^ prev[i+1] for i in range(len(prev)-1)]
        triangle.append(next_row)
    coeffs = [row[0] for row in triangle]
    return coeffs

def zhegalkin_to_string(variables, coeffs):
    terms = []
    for i, c in enumerate(coeffs):
        if c == 1:
            if i == 0:
                terms.append("1")
            else:
                bin_repr = format(i, f"0{len(variables)}b")
                term_vars = [variables[j] for j, bit in enumerate(bin_repr) if bit == '1']
                terms.append("".join(term_vars))
    return " ⊕ ".join(terms) if terms else "0"