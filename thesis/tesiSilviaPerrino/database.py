#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo import MongoClient

# Create a MongoClient to the running mongod instance

client = MongoClient('localhost', 27017)  # connect on the specified host and port
print 'Db connected on port 27017 . . .'

# Database
db = client.ProvaPyMongo
# db = client.ProvaPyMongo
print 'Db -> ProvaPyMongo'

# Collection
metadati = db.metadati
dati = db.dati
cose = db.cose
test_set = db.test_set
