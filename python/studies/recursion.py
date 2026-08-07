def matryoshka(n):
  if n == 1:
    print("Matryoshka")
  else:
    print("Top of the Matryoshka n=", n)
    matryoshka(n-1)
    print("Bottom of the Matryoshka n=", n)
matryoshka(5)
#print(matryoshka) # object <function matryoshka at 0x7f8e2c3d1b80>
