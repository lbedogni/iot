
arr = []
with open("coppieInputClasse.csv", 'r') as coppie:
	for line in coppie.readlines():
		arr.append(line.strip().split(",")[1])
		
arr = list(set(arr))

print len(arr)
print arr
