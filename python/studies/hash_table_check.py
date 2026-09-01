import time

N = 10_000_000

# List
arr = list(range(N))
# Dict
data = {i: True for i in range(N)}

target = N - 1

# searching list
start = time.perf_counter()
target in arr
end = time.perf_counter()
print(f"list: {end - start:.6f} сек")


# searching dict
start = time.perf_counter()
target in data
end = time.perf_counter()
print(f"dict: {end - start:.6f} сек")

#
# Python .\hash_table_check.py
#list: 0.075207 сек
#dict: 0.000003 сек
#