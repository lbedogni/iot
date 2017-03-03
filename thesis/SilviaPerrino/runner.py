import subprocess, sys

open("risultati.csv", "w").close()

for x in range(10):
	for y in range(10):
		print x,y
		process = subprocess.Popen(["python", "clusteringDictionaryEsteso.py", str(x*10), str(y*10)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		process.wait()
