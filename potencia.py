b = int(raw_input("Escriba el valor de la base: "))
e = int(raw_input("Escriba el valor de la exponente: "))

p=b
for i in range(1,e):

	p=p*b
print str(b)+" elevado a la "+str(e)+" es "+str(p)
