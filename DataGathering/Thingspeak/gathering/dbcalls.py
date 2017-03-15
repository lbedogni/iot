import MySQLdb
import dbsettings
from datetime import datetime

db = None
cur = None

MAX_LIMIT = 10000
MIN_LIMIT = 500
ADD_LIMIT = 100

# Init Database connection
def init():
	global db
	global cur
	
	s = dbsettings.dbSet
	db = MySQLdb.connect(host=s['host'], user=s['user'], passwd=s['passwd'], db=s['db'])
	cur = db.cursor()

# Close Database connection
def finish():
	global db
	db.close()

# Get all devices owned by a certain participant
def findAllDevices(participant):
	devices = []
	try:
		cur.execute("SELECT `ID`,`daycount` FROM `Devices` WHERE (`participant_ID` = '" + participant + "')")
		for dev in cur.fetchall():
			d = {}
			d['id'] = int(dev[0].split("_")[1])
			d['daycount'] = int(dev[1])
			devices.append(d)
	except:
		return None
	return devices

# Get and set the next index in thingspeak to be fetched for new metadata
def getThingspeakNextChannel():
	try:
		cur.execute("SELECT `Value` FROM `Global` WHERE (`VarName` = 'TS_COUNTER')")
		return int(cur.fetchall()[0][0])
	except:
		return -1
def setThingspeakNextChannel(value):
	try:
		cur.execute("UPDATE `Global` SET `Value` = '" + str(value) + "' WHERE (`VarName` = 'TS_COUNTER')")
		db.commit()
	except:
		db.rollback()
		
# Set the daycount for a specific Device
def setDayCount(ID, newVal):
	try:
		cur.execute("UPDATE `Devices` SET `daycount`='" + newVal + "' WHERE (`ID`='" + ID + "')")		
		db.commit()
	except:
		db.rollback()
		
def calculateDaycount(start, end):
	start_time = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
	end_time = datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
	return min(max(0, ((end_time - start_time).days - 1)), 30)
	
# Get the next channel to be examined at this round (saved into a file)
# Also get how many channels we are about to examine
def getNextChannel(participant):
	try:
		with open("NXT_" + participant, 'r') as f:
			start = f.readline().strip()
			limit = f.readline().strip()
			return int(start), int(limit)
	except:
		print "No file found or bad recording format"
		return 0, MIN_LIMIT

# Set the next channel to be examined at the next round	(saved into a file)
# Also set how many channels to examine next time (to be increased only if no channels were examined last time)
def setNextChannel(participant, value):
	oldstart, oldlimit = getNextChannel(participant)
	if oldstart == value:
		limit = oldlimit + ADD_LIMIT
		if limit > MAX_LIMIT:
			limit = MAX_LIMIT
	else:
		limit = MIN_LIMIT
		
	with open("NXT_" + participant, 'w') as f:
		f.write(str(value) + "\n" + str(limit))
		
def esc(word):
	return word.replace("'", "\\'")

# Convert ThingSpeak Datetime to DB datetime format
def TSToDatetime(string_datetime):
	return string_datetime.replace("T"," ").replace("Z","")

# Check if the device exists	
def IsDevice(device_ID):
	cur.execute("SELECT * FROM `Devices` WHERE ID = '" + device_ID + "'")
	duplicate = len(cur.fetchall())
	return (duplicate > 0)
	
# Insert a device in the DB
def insertDevice(device_ID, device_name, device_type, participant_id, daycount):
	
	try:
		cur.execute("INSERT INTO `Devices` (`ID`, `name`, `device_type`, `participant_ID`, `daycount`) VALUES ('" + device_ID + "', '" + esc(device_name) + "', '" + device_type + "', '" + participant_id + "', '" + daycount + "');")
		db.commit()
	except:
		print "error"
		db.rollback()

# Insert a stream in the DB and get back its ID
def insertStream(stream_name, stream_class, creation_timestamp, description, elevation, url, device_ID):
	
	try:
		int(elevation)
	except:
		elevation = "0"
	stream_id = ""
	try:
		cur.execute("INSERT INTO `DataStreams`(`name`, `data_class`, `creation_timestamp`, `description`, `elevation`, `url`, `last_entry_ID`, `device_ID`) VALUES ('" + esc(stream_name) + "','" + stream_class + "','" + creation_timestamp + "','" + esc(description) + "','" + elevation + "','" + esc(url) + "','" + str(-1) + "','" + device_ID + "');")
		
		db.commit()
		cur.execute("SELECT `ID` FROM `DataStreams` WHERE (name = '" + esc(stream_name) + "') AND (device_ID = '" + device_ID + "')")
		stream_id = str(cur.fetchall()[0][0])
	except:
		print "error"
		db.rollback()
	return stream_id

# Insert a Measurement in the DB	
def insertMeasurement(stream_id, lat, lon, value, timestamp):
	print timestamp
	cur.execute("INSERT INTO `Measurements`(`data_stream_ID`, `GPS_latitude`, `GPS_longitude`, `MGRS_coordinates`, `value`, `timestamp`) VALUES ('" + stream_id + "','" + lat + "','" + lon + "','0','" + value + "','" + timestamp + "')")
	try:
		db.commit()
	except:
		db.rollback()
		
# Insert a Measurement in the DB	
def insertMultipleMeasurements(valuesString):
	print "about to insert stuff"
	cur.execute("INSERT INTO `Measurements`(`data_stream_ID`, `GPS_latitude`, `GPS_longitude`, `MGRS_coordinates`, `value`, `timestamp`) VALUES " + valuesString + ";")
	try:
		db.commit()
		print "done"
	except:
		db.rollback()
		print "noooooo"
		
# Insert a Measurement in the DB	
def insertMultipleMeasurementsReduced(valuesString):
	print "about to insert stuff"
	cur.execute("INSERT INTO `Measurements`(`data_stream_ID`, `value`, `timestamp`) VALUES " + valuesString + ";")
	try:
		db.commit()
		print "done"
	except:
		db.rollback()
		print "noooooo"
		
# Update a stream with its last entry id and last update timestamp
def refreshStream(stream_id):
	cur.execute("SELECT MAX(`ID`), `timestamp` FROM `Measurements` WHERE (`data_stream_ID` = '" + stream_id + "') GROUP BY `data_stream_ID`")
	results = cur.fetchall()
	meas_id = str(results[0][0])
	timestamp = str(results[0][1])
	cur.execute("UPDATE `DataStreams` SET `last_entry_ID`='" + meas_id + "', `last_update_timestamp`='" + timestamp + "' WHERE (ID = '" + stream_id + "')")
	try:
		db.commit()
	except:
		db.rollback()
		
# Update a stream with its last entry id and last update timestamp
def refreshStreamSimple(stream_id, timestamp):
	sql = "UPDATE `DataStreams` SET `last_update_timestamp`='" + timestamp + "' WHERE (ID = '" + stream_id + "')"
	cur.execute(sql)
	try:
		db.commit()
	except:
		db.rollback()
	
# Get the last update from a device (from one of its streams)	
def getLastUpdate(device_id):
	try:
		cur.execute("SELECT `last_update_timestamp` FROM `DataStreams` WHERE (`device_ID` = '" + device_id + "')")
		results = cur.fetchall()
		if len(results) > 0:
			return results[0][0]
		else:
			return None 
	except:
		print "getLastUpdate FAILED"
		return None
		
def getDataStream(device_id, name):
	try:	
		cur.execute("SELECT `ID` FROM `DataStreams` WHERE (`device_id` = '" + device_id + "' AND `name` = '" + name + "')")
		results = cur.fetchall()
		if len(results) > 0:
			return int(results[0][0])
		else:
			return None
	except:
		print "getDataStream FAILED"
		return None
			
