import MySQLdb
import sys
import datetime

class MyDB(object):
    _db_connection = None
    _db_cur = None

    def __init__(self):
        self._db_connection = MySQLdb.connect("localhost","tirocinioLAM","LAM1516!","TestTrainingSet" )
        self._db_cur = self._db_connection.cursor()

    def get_training_set(self,classe):
        query = u'Select Distinct Field_name\
                  From Field\
                  Where SetType="Training" and Class="{}"'.format(classe)
        response = self._db_cur.execute(query)
        self._db_connection.commit()
        return self._db_cur.fetchall()

    def get_all_streams(self):
        query = u'Select Field.Id,Field.Field_name,Field.Class,Channel.Description,Channel.Name,Channel.Id\
                  From Field Inner Join Channel on Field.Channel_id = Channel.Id\
                  Where Class<>"Uncertainly" and Class<>"Class"'

        response = self._db_cur.execute(query)
        self._db_connection.commit()
        data = self._db_cur.fetchall()
        dict = []
        for item in data:
            dict.append({'field_id': item[0],'field_name':item[1],'field_class':item[2],'channel_description':item[3],'channel_name':item[4],'channel_id':item[5]})

        return dict

    def get_relevant_streams(self):
        query = u'Select Field.Id,Field.Field_name,Field.Class,Channel.Description,Channel.Name,Channel.Id\
                  From Field Inner Join Channel on Field.Channel_id = Channel.Id\
                  Where Class In ("Temperature","Dust_Level","Gas_Level","Brightness","Power","UV","Heat_Index","Pressure",\
                  "Rain_Index", "Radiation", "Humidity", "Wind_Direction", "Wind_Speed") '

        response = self._db_cur.execute(query)
        self._db_connection.commit()
        data = self._db_cur.fetchall()
        dict = []
        for item in data:
            dict.append({'field_id': item[0],'field_name':item[1],'field_class':item[2],'channel_description':item[3],'channel_name':item[4],'channel_id':item[5]})

        return dict

    def get_test_set(self):
        query = u'Select Field.Id,Field.Field_name,Field.Class,Channel.Description,Channel.Name,Channel.Id\
                  From Field Inner Join Channel on Field.Channel_id = Channel.Id\
                  Where SetType="Test" and Class<>"Uncertainly" and Class<>"Class"'

        response = self._db_cur.execute(query)
        self._db_connection.commit()
        data = self._db_cur.fetchall()
        dict = []
        for item in data:
            dict.append({'field_id': item[0],'field_name':item[1],'field_class':item[2],'channel_description':item[3],'channel_name':item[4],'channel_id':item[5]})

        return dict

    def getFieldTags(self, channel_id):
        query = u'SELECT Tag_name\
                  FROM TagChannel\
                  WHERE Channel_id = "{}"'.format(channel_id)
        response = self._db_cur.execute(query)
        self._db_connection.commit()
        data = self._db_cur.fetchall()
        dict = []
        for tag in data:
            dict.append(tag[0])
        
        return dict

    def store_classification(self, field,attriubuted_class,distance,number,table):
        query = u'INSERT INTO {} (Field_id,Field_name,Field_class,Channel_name,Channel_description,Attributed_class,Distance,Channel_id,Number)\
                VALUES("{}","{}","{}","{}","{}","{}",{},"{}",{})'.format(table,field["field_id"],field["field_name"],field["field_class"],field["channel_name"],field["channel_description"],attriubuted_class,distance,field["channel_id"],number)
        
        response = self._db_cur.execute(query)
        self._db_connection.commit()
        return self._db_cur.fetchone()
            
    def delete_classification(self,table):
        query = u'DELETE FROM {}'.format(table)
        
        response = self._db_cur.execute(query)
        self._db_connection.commit()
        return self._db_cur.fetchone() 

    def store_metric(self, metric,classe,timestamp,number,table):
        query = u'INSERT INTO {} (Class,Recall,Precisions,F_measure,M_timestamp,Number)\
                VALUES("{}",{},{},{},"{}",{})'.format(table,classe,metric["recall"],metric["precision"],metric["f_measure"],timestamp,number)
        
        response = self._db_cur.execute(query)
        self._db_connection.commit()
        return self._db_cur.fetchone()

    def delete_metrics(self,table):
        query = u'DELETE FROM {}'.format(table)

        response = self._db_cur.execute(query)
        self._db_connection.commit()
        return self._db_cur.fetchone()

    def store_matrix(self, classe,row,table):
        row = '"' + classe + '", ' + row 
        query = u'INSERT INTO ' +  table + ' VALUES(' + row + ')'
        
        response = self._db_cur.execute(query)
        self._db_connection.commit()
        return self._db_cur.fetchone()
        

    def delete_matrix(self,table):
        query = u'DELETE FROM ' + table

        response = self._db_cur.execute(query)
        self._db_connection.commit()
        return self._db_cur.fetchone()


    def __del__(self):
self._db_connection.close()
