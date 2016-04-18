dic = open("ellipsys.txt", "a")
a="CPE#"
for i in range(0,1000000):
	i=i+1
	b=str(i).zfill(6)
	dic.write(a+b);
dic.close()
print "listo"
