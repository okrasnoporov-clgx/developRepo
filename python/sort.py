def insert_sort(A):
  """ insert sort """
  pass

def choise_sort(A):
  """ choice sort """
  pass

def bubble_sort(A):
  """ bubble sort """
  pass

def test_sort (sort_algorithm):
  print("testCase #1: ", end="")
  A = [4, 2, 5, 1, 3]
  A_sorted = [1, 2, 3, 4, 5]
  sort_algorithm(A)
  print("OK" if A == A_sorted else "Fail")
  
  #if A == A_sorted:
  #  print("Ok")
  #else:
  #  print("Fail")
  
