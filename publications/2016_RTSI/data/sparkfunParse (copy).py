import sys
import urllib.request
import binascii
from bs4 import BeautifulSoup
from googlemaps import Client

maxPages = int(sys.argv[1])
pageArray = []
gmaps = Client("AIzaSyACiNaspKQH8lTCJenBSTQ9YWKy3sAw1AM")

for i in range(maxPages):
	page = i
	print(i)
	try:	
		pageArray.append(urllib.request.urlopen("https://data.sparkfun.com/streams/?page=" + str(page)))
	except:
		print (sys.exc_info()[0])
		continue
		
print ("LENGTH = " + str(len(pageArray)))

# record is: streamcode, streamname, GPS, tags
record = ["","","","",[]]
city = ["","",""]
for html in pageArray:
	
	for l in html.readlines():
		line = l.decode('utf-8').strip()
		if "stream-title" in line:
			if not record[0] == "":
				address = ", ".join(city)
				#sys.exit()
				if not address == ", , ":
					geocoord = gmaps.geocode(address)[0]['geometry']['location']
					lat = str(geocoord['lat'])
					lng = str(geocoord['lng'])
					
					record[2] = lat
					record[3] = lng
					#gmaps.geocode(address)
				tags = ", ".join(record[4])
				fw = open('dataSparkfun.csv','a+')
				fw.write(", ".join(record[:4]) + ", " + str(tags) + '\n')
				fw.close()
			 
			#Azerare
			record = ["","","","",[]]
			city = ["","",""]
			
			# Nuova roba
			stream = line.split("\"")[3]
			record[0] = stream
			name = line.split(">")[2].split("<")[0]
			record[1] = name
		if "/streams/city" in line:
			city[0] = line.split("/streams/city/")[1].split("\"")[0]
		if "/streams/state" in line:
			city[1] = line.split("/streams/state/")[1].split("\"")[0]		
		if "/streams/country" in line:
			city[2] = line.split("/streams/country/")[1].split("\"")[0]
		if "/streams/tag" in line:
			record[4].append(line.split("/streams/tag/")[1].split("\"")[0])
