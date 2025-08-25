def insert_sort(A):
  """ insert sort """
  N = len(A)
  for top in range (1, N):
    k = top
    while k > 0 and A[k-1] > A[k]:
      A[k], A[k-1] = A[k-1], A[k]
      k -= 1
      
  pass

def choise_sort(A):
  """ choice sort """
  N = len(A)
  for pos in range(0, N-1):
    for k in range(pos+1, N):
      if A[k] < A[pos]:
        A[k], A[pos] = A[pos], A[k]
  pass

def bubble_sort(A):
  """ bubble sort """
  pass

def test_sort (sort_algorithm):
  print("Testing: ", sort_algorithm.__doc__)
  print("testCase #1: ", end="")
  A = [4, 2, 5, 1, 3]
  A_sorted = [1, 2, 3, 4, 5]
  sort_algorithm(A)
  print("OK" if A == A_sorted else "Fail")

  print("testCase #2: ", end="")
  A = list(range(10, 20)) + list(range(0, 10))
  A_sorted = list(range(20))
  sort_algorithm(A)
  print("OK" if A == A_sorted else "Fail")

  print("testCase #3: ", end="")
  A = [4, 2, 4, 2, 1]
  A_sorted = [1, 2, 2, 4, 4]
  sort_algorithm(A)
  print("OK" if A == A_sorted else "Fail")
  
  #if A == A_sorted:
  #  print("Ok")
  #else:
  #  print("Fail")

if __name__ == "__main__":
  test_sort(insert_sort)
  test_sort(choise_sort)
  test_sort(bubble_sort)

