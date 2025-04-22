base=2
x = int(input())
prdigit=''
while x > 0:
  prdigit = str(x % base) + prdigit
  x=x//base
print (prdigit)
