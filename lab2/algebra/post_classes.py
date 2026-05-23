def is_T0(table):
    return table[0][1] == 0

def is_T1(table):
    return table[-1][1] == 1

def is_self_dual(table):
    n = len(table)
    for i in range(n):
        if table[i][1] == table[n - i - 1][1]:
            return False
    return True

def is_monotone(variables, table):
    for i, (ctx1, val1) in enumerate(table):
        for j, (ctx2, val2) in enumerate(table):
            le = all(ctx1[var] <= ctx2[var] for var in variables)
            if le and val1 > val2:
                return False
    return True

def is_linear(zhegalkin_coeffs):
    for i, coeff in enumerate(zhegalkin_coeffs):
        if coeff == 1 and bin(i).count('1') > 1:
            return False
    return True