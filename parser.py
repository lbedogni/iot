#!/usr/bin/python3
from urllib.request import urlopen
import json
import sys
from urllib.error import HTTPError

f_meta = open('metaFromTS.csv','a+')
f_data = open('dataFromTS.csv','a+')
f_erro = open('erroFromTS.csv','a+')
f_keys = open('keysFromTS.csv','a+')
        
keyArray = ['description','elevation','name','created_at','updated_at','longitude','latitude','last_entry_id','id']

for i in range(100000,101000):
    ff = "https://thingspeak.com/channels/" + str(i) + "/feed.json"
    print(ff)
    f = ""
    jj = ""
    try:
        f = urlopen("https://thingspeak.com/channels/" + str(i) + "/feed.json").read().decode("utf-8")
        jj = json.loads(f)

        chan = jj['channel']
        for item in chan.keys():
            if item.startswith('field'):
                f_data.write(str(i) + ',' + str(item) + ',' + str(chan[item]) + '\n')
            elif item not in keyArray:
                f_keys.write(str(i) + ',' + str(item) + ',' + str(chan[item]) + '\n')
        for item in keyArray:
            if item not in chan.keys():
                chan[item] = ""

        f_meta.write(",".join([str(i),chan['name'].replace(",",";").replace("\n",""),chan['description'].replace(",",";").replace("\n",""),chan['created_at'],chan['updated_at'],chan['longitude'],chan['latitude'],chan['elevation'],str(chan['last_entry_id'])]))
        f_meta.write('\n')

    except KeyError:
        f_erro.write(str(jj['channel'].keys()) + '\n')
    except HTTPError:
        pass
    except:
        print(sys.exc_info()[0])
        print(chan)

f_meta.close()
f_data.close()
f_erro.close()
f_keys.close()
