def matryoshka(n):
  if n == 1:
    print("Matryoshka")
  else:
    print("Top of the Matroshka n=", n)
    matryoshka(n-1)
    print("Bottom of the Matroshka n=", n)

