#!/usr/bin/python3
import urllib.request
import sys
try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

PROV = sys.argv[1]
DATS = sys.argv[2]
DATE = sys.argv[3]

# Full string is http://www.arpae.it/estraistaz.asp?q=8&i=19.10.2016&f=19.10.2016&s=3000001&p=RE
BASE_STR = "http://www.arpae.it/estraistaz.asp?q="

def compose(q):
    return BASE_STR + str(q) + "&i=" + str(DATS) + "&f=" + str(DATE) + "&s=3000001&p=" + str(PROV)

rawdata = BeautifulSoup(urllib.request.urlopen("http://www.arpae.it/v2_rete_di_monitoraggio.asp?p=RE&idlivello=1637").read(), 'html.parser')
items = rawdata.find('div', {'id':'dettaglio'}).p.findAll()
ii = str(items[1]).split("<br>")
lat = lng = -1
for item in ii:
    if "Latitudine" in str(item):
        lat = item.split("</b>")[1].strip()
    if "Longitudine" in str(item):
        lng = item.split("</b>")[1].strip()

qq = range(10)
print("Lat is " + str(lat) + ", Lon is " + str(lng))
for q in qq:
    try:
        rawdata = BeautifulSoup(urllib.request.urlopen(compose(q)).read(), 'html.parser')
        ii = rawdata.find("tbody").findAll("tr")
    except:
        continue
    for i in ii:
        items = i.findAll("td")

        name = str(items[0].text)
        dates = str(items[1].text)
        datee = str(items[2].text)
        instr = str(items[3].text)
        value = str(items[4].text)
        unit = str(items[5].text)

        print(",".join([name,dates,datee,instr,value,unit]))
