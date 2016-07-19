#!/usr/bin/python3
import sys
import time
import datetime

ff = open(sys.argv[1],'r')
fw = open(sys.argv[2],'w+')
column = int(sys.argv[3])
for line in ff.readlines():
    myLine = line.replace("\r","")
    print(myLine)
    ll = line.replace("\r"," ").strip().split(",")
    print(line.replace("\r"," "))
    print(ll)
    ttCreate = ll[column].replace("T"," ").replace("Z","").strip()
    tt = time.mktime(datetime.datetime.strptime(str(ttCreate), "%Y-%m-%d %H:%M:%S").timetuple())
    print(tt)
    fw.write(str(tt) + "\n")

ff.close()
fw.close()
