def f (n:int):
    assert n >= 0, "Input must be a non-negative integer"
    if n == 0:
        return 1
    return n * f(n-1)
print(f(5))


