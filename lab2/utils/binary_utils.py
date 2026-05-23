def int_to_bin(n, size):
    return format(n, f'0{size}b')

def count_ones(n):
    return bin(n).count('1')

def differs_by_one_bit(a, b):
    diff = 0
    for x, y in zip(a, b):
        if x != y:
            diff += 1
    return diff == 1