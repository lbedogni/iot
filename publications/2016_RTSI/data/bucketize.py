#!/usr/bin/python3
import sys

ff = open(sys.argv[1],'r')
fw = open(sys.argv[2],'w+')
buckets = int(sys.argv[3])

initial = -1
counter = 0
for line in ff.readlines():
    dd = float(line.strip())
    if initial == -1:
        initial = dd
    if dd <= initial + buckets:
        counter += 1
    if dd > initial + buckets:
        # Bucket finished
        fw.write(str(initial) + " " + str(counter) + '\n')
        counter = 1
        initial = dd
ff.close()
fw.close()
