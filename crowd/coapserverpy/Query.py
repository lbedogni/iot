# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# This file is part of Crowdroid(sense)/Servercoap project, thesis in Crowdsensing.
# Copyright (C) 2016 Alain Di Chiappari

import mysql.connector

TYPE_AMPLITUDE = 100
TYPE_WIFI = 101
TYPE_TEL = 102

class Query:
    conn = None
    cursor = None

    def __init__(self):
        db, user, passw, host = tuple(map(lambda x:x.strip("\n").split(":")[1], open("auth.txt", "r").readlines()))
        self.conn = mysql.connector.connect(user=user, password=passw, database=db, host=host)

###############################################################################
######################### GET QUERIES
###############################################################################

    def getStakeholders(self):
        try:
            self.cursor = self.conn.cursor()
            res = self.cursor.execute("SELECT * FROM stakeholders")
            return self.cursor
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def getSubscribedStakeholders(self, id_user):
        try:
            self.cursor = self.conn.cursor()
            res = self.cursor.execute("SELECT DISTINCT id_stakeholder,name FROM subscription LEFT JOIN stakeholders ON subscription.id_stakeholder=stakeholders.id WHERE id_user=%s",(id_user,))
            return self.cursor
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def getSubscriptionByUserAndSensor(self, id_user, sensor):
        try:
            self.cursor = self.conn.cursor()
            res = self.cursor.execute("SELECT * FROM subscription WHERE id_user=%s AND sensor=%s", (id_user, sensor))
            return self.cursor
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def getAllRules(self):
        try:
            self.cursor = self.conn.cursor()
            res = self.cursor.execute("SELECT * FROM rules")
            return self.cursor
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def getAllStakeholdersRulesForSensor(self, sensor, stakeholder):
        try:
            self.cursor = self.conn.cursor()
            res = self.cursor.execute("SELECT * FROM stakeholders_rules WHERE type=%s AND stakeholder_id=%s", (sensor,stakeholder))
            return self.cursor
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def getAllRulesForSensor(self, sensor):
        try:
            self.cursor = self.conn.cursor()
            res = self.cursor.execute("SELECT * FROM rules WHERE type=%s", (sensor,))
            return self.cursor
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def getSensingForSensorByTimeAndZone(self, sensor, timeStart, zone, granularity):
        try:
            self.cursor = self.conn.cursor()
            gridsq, bigsq, x, y = zone[:3], zone[3:5], zone[5:10], zone[10:15]
            x,y = x[:granularity], y[:granularity]
            table = "all_wifi_data" if sensor == TYPE_WIFI else "all_tel_data" if sensor == TYPE_TEL else "all_sensor_data"
            query = "SELECT * FROM "+table+" WHERE mgrs REGEXP '"+gridsq+bigsq+x+"[[:digit:]]{%s}"+y+"[[:digit:]]{%s}' AND timestamp >= %s"
            #print("getSensingForSensorByTimeAndZone: ",query)
            if sensor != TYPE_TEL and sensor != TYPE_WIFI:
                query += " AND type = %s"
                res = self.cursor.execute(query, (5-granularity, 5-granularity, timeStart, sensor))
            else:
                res = self.cursor.execute(query, (5-granularity, 5-granularity, timeStart))
            return self.cursor
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def getAllSensors(self):
        try:
            self.cursor = self.conn.cursor()
            res = self.cursor.execute("SELECT * FROM sensors")
            return self.cursor
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    # TODO Add WHERE all_sensor_data.timestamp >= subscription.timestamp
    # def getSensorDataForStakeholders(self, id_stakeholder, sensor):
    #     try:
    #         self.cursor = self.conn.cursor()
    #         res = self.cursor.execute("SELECT * FROM all_sensor_data LEFT JOIN subscription ON all_sensor_data.user = subscription.id_user AND all_sensor_data.type = subscription.sensor  WHERE subscription.id_stakeholder = %s AND subscription.sensor = %s", (id_stakeholder, sensor))
    #         return self.cursor
    #     except mysql.connector.Error as err:
    #         print("DB ERROR: {}".format(err))

    def getSensorDataForStakeholders(self, id_stakeholder, sensor):
        try:
            self.cursor = self.conn.cursor()

            table = "all_wifi_data" if sensor == TYPE_WIFI else "all_tel_data" if sensor == TYPE_TEL else "all_sensor_data"

            if sensor != TYPE_TEL and sensor != TYPE_WIFI:
                query = "SELECT * FROM all_sensor_data LEFT JOIN subscription ON all_sensor_data.user = subscription.id_user AND all_sensor_data.type = subscription.sensor  WHERE subscription.id_stakeholder = %s AND subscription.sensor = %s"
            else:
                query = "SELECT * FROM "+table+" LEFT JOIN subscription ON "+table+".user = subscription.id_user WHERE subscription.id_stakeholder = %s AND subscription.sensor = %s"

            res = self.cursor.execute(query, (id_stakeholder, sensor))

            return self.cursor
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))



###############################################################################
######################### INSERT QUERIES
###############################################################################

    def insertStakeholder(self, name):
        try:
            self.cursor = self.conn.cursor()
            query = "INSERT INTO stakeholders(name) VALUES (%s)"
            res = self.cursor.execute(query, (name,))
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def insertSubscription(self, id_user, id_stakeholder, sensor):
        try:
            self.cursor = self.conn.cursor()
            query = "INSERT INTO subscription(id_user, id_stakeholder, sensor) VALUES (%s, %s, %s)"
            res = self.cursor.execute(query, (id_user, id_stakeholder, sensor))
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def insertStakeholderRule(self, sensor, stakeholder_id, description, name, mgrs_area, granularity, expire_count, expire_time, sample_time, timestamp):
        try:
            self.cursor = self.conn.cursor()
            query = "INSERT INTO rules(type, stakeholder_id, description, name, mgrs_area, granularity, expire_count, expire_time, sample_time, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
            res = self.cursor.execute(query, (sensor, stakeholder_id, description, name, mgrs_area, granularity, expire_count, expire_time, sample_time, timestamp))
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def insertRule(self, sensor, name, mgrs_area, granularity, expire_count, expire_time, sample_time, timestamp):
        try:
            self.cursor = self.conn.cursor()
            query = "INSERT INTO rules(type, name, mgrs_area, granularity, expire_count, expire_time, sample_time, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            res = self.cursor.execute(query, (sensor, name, mgrs_area, granularity, expire_count, expire_time, sample_time, timestamp))
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def insertInAllSensorData(self, user, sensor, latitude, longitude, mgrs, value, timest):
        try:
            self.cursor = self.conn.cursor()
            query = "INSERT INTO all_sensor_data(user, type, latitude, longitude, mgrs, value, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            res = self.cursor.execute(query, (user, sensor, latitude, longitude, mgrs, value, timest))
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def insertInAllWifiData(self, user, ssid, latitude, longitude, mgrs, bssid, strength, timestamp):
        try:
            self.cursor = self.conn.cursor()
            query = "INSERT INTO all_wifi_data(user, ssid, latitude, longitude, mgrs, bssid, strength, timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            res = self.cursor.execute(query, (user, ssid, latitude, longitude, mgrs, bssid, strength, timestamp))
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def insertInAllTelData(self, user, latitude, longitude, mgrs, timestamp, strength, operator, tech, throughput):
        try:
            self.cursor = self.conn.cursor()
            query = "INSERT INTO all_tel_data(user, latitude, longitude, mgrs, timestamp, strength, operator, tech, throughput) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            res = self.cursor.execute(query, (user, latitude, longitude, mgrs, timestamp, strength, operator, tech,throughput))
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

###############################################################################
######################### DELETE QUERIES
###############################################################################

    def deleteRuleById(self, value):
        try:
            self.cursor = self.conn.cursor()
            query = "DELETE FROM rules WHERE id=%s"
            res = self.cursor.execute(query, (value,))
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def deleteOldRules(self, timestamp):
        try:
            self.cursor = self.conn.cursor()
            query = "DELETE FROM rules WHERE expire_time<=%s"
            res = self.cursor.execute(query, (timestamp,))
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def deleteOldRulesAndGetThem(self, timestamp):
        try:
            self.cursor = self.conn.cursor()
            queryS = "SELECT * FROM rules WHERE expire_time<=%s"
            res = self.cursor.execute(queryS, (timestamp,))
            deleted = list(self.cursor)

            queryD = "DELETE FROM rules WHERE expire_time<=%s"
            res = self.cursor.execute(queryD, (timestamp,))
            return deleted
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    # If sensor -1 delete all
    def deleteSubscription(self, id_user, id_stakeholder, sensor):
        try:
            self.cursor = self.conn.cursor()
            if sensor == -1:
                query = "DELETE FROM subscription WHERE id_user=%s AND id_stakeholder=%s"
                res = self.cursor.execute(query, (id_user,id_stakeholder))
            else:
                query = "DELETE FROM subscription WHERE id_user=%s AND id_stakeholder=%s AND sensor=%s"
                res = self.cursor.execute(query, (id_user,id_stakeholder,sensor))
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))

    def deleteAllSubscriptionForUser(self, id_user):
        try:
            self.cursor = self.conn.cursor()
            query = "DELETE FROM subscription WHERE id_user=%s"
            res = self.cursor.execute(query, (id_user,))
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))


###############################################################################
###############################################################################

    def close(self):
        try:
            self.cursor.close()
            self.conn.commit()
            self.conn.close()
        except mysql.connector.Error as err:
            print("DB ERROR: {}".format(err))
