from utils.binary_utils import differs_by_one_bit
from itertools import combinations


def combine(a, b):
    diff = 0
    res = []
    for x, y in zip(a, b):
        if x == y:
            res.append(x)
        else:
            res.append('-')
            diff += 1
    return ''.join(res) if diff == 1 else None


def get_minterms(table):
    return [i for i, (_, val) in enumerate(table) if val == 1]


def minterm_to_bin(minterm, n):
    return format(minterm, f'0{n}b')


def quine_mccluskey(variables, table):
    n = len(variables)
    minterms = get_minterms(table)
    if not minterms:
        return []

    groups = {}
    for m in minterms:
        b = minterm_to_bin(m, n)
        ones = b.count('1')
        groups.setdefault(ones, []).append(b)

    prime_implicants = set()
    used = set()
    changed = True
    while changed:
        changed = False
        new_groups = {}
        for ones in sorted(groups.keys()):
            if ones + 1 not in groups:
                continue
            for a in groups[ones]:
                for b in groups[ones + 1]:
                    c = combine(a, b)
                    if c:
                        new_groups.setdefault(c.count('1'), []).append(c)
                        used.add(a)
                        used.add(b)
                        changed = True

        for ones, lst in groups.items():
            for term in lst:
                if term not in used:
                    prime_implicants.add(term)
        groups = new_groups
        used = set()

    prime_implicants = list(prime_implicants)
    minterm_bins = [minterm_to_bin(m, n) for m in minterms]

    coverage = {}
    for pi in prime_implicants:
        covers = []
        for i, mt in enumerate(minterm_bins):
            if all(pi[j] == '-' or pi[j] == mt[j] for j in range(n)):
                covers.append(i)
        coverage[pi] = covers

    uncovered = set(range(len(minterms)))
    selected = []
    while uncovered:
        best_pi = None
        best_cover = set()
        for pi, covers in coverage.items():
            cover_set = set(covers) & uncovered
            if len(cover_set) > len(best_cover):
                best_cover = cover_set
                best_pi = pi
        if best_pi is None:
            break
        selected.append(best_pi)
        uncovered -= best_cover

    return selected


def implicant_to_term(implicant, variables):
    literals = []
    for i, ch in enumerate(implicant):
        if ch == '1':
            literals.append(variables[i])
        elif ch == '0':
            literals.append(f"!{variables[i]}")
    return " & ".join(literals) if literals else "1"


def minimize_dnf(variables, table):
    implicants = quine_mccluskey(variables, table)
    terms = [implicant_to_term(imp, variables) for imp in implicants]
    return " | ".join(terms) if terms else "0"