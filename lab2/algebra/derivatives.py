def partial_derivative(ast, context_list, var):
    result = []
    for context, _ in context_list:
        c0 = context.copy()
        c1 = context.copy()
        c0[var] = 0
        c1[var] = 1
        val = ast.evaluate(c0) ^ ast.evaluate(c1)
        result.append(val)
    return result

def mixed_derivative(ast, table, var_list):
    result = []
    for context, _ in table:
        from itertools import product
        combos = list(product([0,1], repeat=len(var_list)))
        xor_sum = 0
        for vals in combos:
            ctx = context.copy()
            for var, val in zip(var_list, vals):
                ctx[var] = val
            xor_sum ^= ast.evaluate(ctx)
        result.append(xor_sum)
    return result