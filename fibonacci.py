penultimo=0
ultimo=1
siguiente=0
s=open("fibonacci.txt", "w")
a=int(raw_input("Escriba la cantidad de numeros que desea mostrar: "))

for i in range(0,a):
        s.write(str(siguiente)+"\n")
        penultimo=ultimo
        ultimo=siguiente
        siguiente=penultimo+siguiente
        i=i+1
s.close()
print "listo"
