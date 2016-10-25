#!/usr/bin/python3
# Usage: ./filename province period-separated-date-start period-separated-date-end
# Example: ./get.py RE 10.10.2016 19.10.2016
import urllib.request
import sys
import pymysql
import traceback
import time

ARPAE_ID = "3"

try:
	from BeautifulSoup import BeautifulSoup
except ImportError:
	from bs4 import BeautifulSoup

PROV = sys.argv[1]
DATS = sys.argv[2]
DATE = sys.argv[3]

# Full string is http://www.arpae.it/estraistaz.asp?q=8&i=19.10.2016&f=19.10.2016&s=3000001&p=RE
BASE_STR = "http://www.arpae.it/estraistaz.asp?q="

# Compose the URL
def compose(q, stat):
	return BASE_STR + str(q) + "&i=" + str(DATS) + "&f=" + str(DATE) + "&s=" + str(stat) + "&p=" + str(PROV)

# It returns the class, the brief name and the long name of the measured parameter
def find_class(raw_string):
	if raw_string == "CO (Monossido di carbonio)":
		return "COPR", "CO", raw_string
	elif raw_string == "PM10":
		return "PM10", "PM10", raw_string
	elif raw_string == "NO2 (Biossido di azoto)":
		return "NO2A", "NO2", raw_string
	elif raw_string == "PM2.5":
		return "PM25", "PM2.5", raw_string
	elif raw_string == "O3 (Ozono)":
		return "O3OZ", "O3", raw_string
	elif raw_string == "C6H6 (Benzene)":
		return "C6H6", "C6H6", raw_string
	elif raw_string == "NOX (Ossidi di azoto)":
		return "NOXO", "NOX", raw_string
	else:
		return "UNKN", "Unknown", raw_string
		
def get_timestamps(beg, end):
	if len(beg.split(" ")) == 1:
		beg += " 00.00.00"
	if len(end.split(" ")) == 1:
		end += " 00.00.00"
	time_beg = time.strptime(beg, "%d/%m/%Y %H.%M.%S")
	time_end = time.strptime(end, "%d/%m/%Y %H.%M.%S")
	
	#int(time.mktime(time_beg)) is in milliseconds
	
	return time.strftime("%Y-%m-%d %H:%M:%S", time_beg), time.strftime("%Y-%m-%d %H:%M:%S", time_end)

rawdata = BeautifulSoup(urllib.request.urlopen("http://www.arpae.it/v2_rete_di_monitoraggio.asp?p="+str(PROV)+"&idlivello=1637").read(), 'html.parser')
items = rawdata.find('div', {'id':'dettaglio'}).p.findAll()
ii = str(items[1]).split("<br>")
lat = lng = -1
for item in ii:
	if "Latitudine" in str(item):
		lat = item.split("</b>")[1].strip()
	if "Longitudine" in str(item):
		lng = item.split("</b>")[1].strip()

stations = rawdata.find('select').findAll('option')

# Open database connection (works only local or tunnel)
db = pymysql.connect("localhost","SenSquare","mgrs32TPQ","SenSquare" )
# prepare a cursor object using cursor() method
cursor = db.cursor()

for stat in stations:
	print("http://www.arpae.it/v2_rete_di_monitoraggio.asp?p="+str(PROV)+"&s="+str(stat.get('value'))+"&idlivello=1637")
	try:
		rawdata = BeautifulSoup(urllib.request.urlopen("http://www.arpae.it/v2_rete_di_monitoraggio.asp?p="+str(PROV)+"&s="+str(stat.get('value'))+"&idlivello=1637").read(), 'html.parser')
		items = rawdata.find('div', {'id':'dettaglio'}).p.findAll()
	except:
		continue

	ii = str(items[1]).split("<br>")
	lat = lng = -1
	for item in ii:
		if "Indirizzo" in str(item):
			dev_id = (PROV + "_" + item.split("</b>")[1].strip())[0:32]
		if "Latitudine" in str(item):
			lat = item.split("</b>")[1].strip()
		if "Longitudine" in str(item):
			lng = item.split("</b>")[1].strip()
	lat = str(lat).replace(',','.')
	lng = str(lng).replace(',','.')
	
	#qq for now 5 7 8 11
	parameters = range(11)
    #print("Lat is " + str(lat) + ", Lon is " + str(lng))
    
	# insert the device if it is not yet registered
	try: 
		cursor.execute("SELECT ID from Devices WHERE (ID = '" + dev_id + "')")
		if len(cursor.fetchall()) == 0:
			cursor.execute("INSERT INTO Devices(ID, name, device_type, participant_ID) \
				VALUES ('%s', '%s', '%s', '%s')" % (dev_id, dev_id, "GOVERN", "3"))
			db.commit()
			print("Device inserted")
		else:
			print("We already got this device")
	except:
		db.rollback()
		print(traceback.format_exc())

	# Process every type of measurement from that station
	for param in parameters:
		try:
			rawdata = BeautifulSoup(urllib.request.urlopen(compose(param, stat.get('value'))).read(), 'html.parser')
			data_rows = rawdata.find("tbody").findAll("tr")
			data_class, data_name, description = find_class(str(rawdata.find("thead").findAll("tr")[0].findAll("th")[4].text))
		except:
			continue
			
		# insert the stream if it is not yet registered
		try: 
			cursor.execute("SELECT ID from DataStreams WHERE (device_ID = '" + dev_id + "' AND data_class = '" + data_class + "')")
			ans = cursor.fetchall()
			if len(ans) == 0:
				stream_name = (data_name + "_" + dev_id)[0:32]
				cursor.execute("INSERT INTO DataStreams(device_ID, name, data_class, last_entry_ID, reliability, accuracy, update_rate, description) \
					VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (dev_id, stream_name, data_class, "-1", "100", "100", "1.0", description))
				db.commit()
				# re-execute the query to get the stream ID
				cursor.execute("SELECT ID from DataStreams WHERE (device_ID = '" + dev_id + "' AND data_class = '" + data_class + "')")
				stream_ID = cursor.fetchall()[0][0]
				print("Stream inserted")
			else:
				stream_ID = ans[0][0]
				print("We already got this stream")
		except:
			db.rollback()
			print(traceback.format_exc())
			
		# Process every row of the table
		last_measurement = 0
		for row in data_rows:
			
			# Get the params of the row
			items = row.findAll("td")
			name = str(items[0].text)
			#~ date_start = str(items[1].text)
			#~ date_end = str(items[2].text)
			date_start, date_end = get_timestamps(str(items[1].text), str(items[2].text))
			instr = str(items[3].text)
			value = str(items[4].text)
			unit = str(items[5].text)
			
			# insert the measurement if it is not yet registered
			try: 
				cursor.execute("SELECT ID from Measurements WHERE (timestamp = '" + date_end + "')")
				if len(cursor.fetchall()) == 0:
					cursor.execute("INSERT INTO Measurements(data_stream_ID, GPS_latitude, GPS_longitude, MGRS_coordinates, value, timestamp) \
						VALUES ('%s', '%s', '%s', '%s', '%s', '%s')" % (stream_ID, lat, lng, "-1", value, date_end))
					db.commit()
					print("Values inserted")
					
					# update the last update timestamp
					cursor.execute("UPDATE DataStreams SET last_update_timestamp = '%s' WHERE ID = '%s'" % (date_end, stream_ID))
					db.commit()
					print("Values updated")
				else:
					print("Values duplicate")
					continue
			except:
				db.rollback()
				print(traceback.format_exc())
			print(",".join([name, lat, lng, str(date_start), str(date_end), instr, value, unit]))
		
		#TODO update stream
		


            
# disconnect from server
db.close()          
