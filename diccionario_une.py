dic = open("ellipsys.txt", 'w')
a="CPE#"
for i in range(0,1000):
	i=i+1
	b=a+str(i).zfill(6)
	dic.write(b+"\n");
for i in range(0,1000000):
	i=i+1
	b=a+str(i).zfill(6)
	dic.write(b+"\n");
dic.close()
print "listo"
