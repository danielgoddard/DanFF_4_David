import numpy

data=open('combined.txt', 'r')
subset=[]
for line in data.readlines()[1:]:
	ln=line.split()
	light_age=float(ln[0])
	subset.append(light_age)
print subset