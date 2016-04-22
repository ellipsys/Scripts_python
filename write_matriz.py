import math
matriz=[]
filas=int(raw_input("Escriba la cantidad de filas: "))
columnas=int(raw_input("Escriba la cantidad de columnas: "))
for i in range(filas):
	matriz.append([0]*columnas)
for f in range(filas):
	for c in range(columnas):
		matriz[f][c]=int(raw_input("Escribe el elemento %d,%d: "%(f,c)))
print matriz
