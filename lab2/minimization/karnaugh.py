def build_karnaugh_map(variables, table):
    n = len(variables)
    values = [v for _, v in table]
    if n == 2:
        return [[values[0], values[1]], [values[2], values[3]]]
    elif n == 3:
        return [[values[0], values[1], values[3], values[2]],
                [values[4], values[5], values[7], values[6]]]
    elif n == 4:
        indices = [0,1,3,2]
        k_map = [[0]*4 for _ in range(4)]
        for i, row_idx in enumerate(indices):
            for j, col_idx in enumerate(indices):
                idx = (row_idx << 2) | col_idx
                if idx < len(values):
                    k_map[i][j] = values[idx]
                else:
                    k_map[i][j] = 0
        return k_map
    elif n == 5:
        indices = [0,1,3,2]
        maps = []
        for e_val in (0,1):
            kmap = [[0]*4 for _ in range(4)]
            for i, row_idx in enumerate(indices):
                for j, col_idx in enumerate(indices):
                    idx = (e_val << 4) | (row_idx << 2) | col_idx
                    if idx < len(values):
                        kmap[i][j] = values[idx]
            maps.append(kmap)
        return maps
    else:
        return values

def minimize_karnaugh(variables, table):
    from minimization.quine_mccluskey import minimize_dnf
    return minimize_dnf(variables, table)