#!/usr/local/bin/python
# coding=utf-8



import xml.etree.ElementTree as ET
import pprint
import re
import codecs
import json
import sys
import datetime

lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

remapCity={"Selfkant-Millen":"Selfkant - Millen","sittard":"Sittard", "Selfkant - Tüdderen":"Selfkant - Tüddern","Selfkant-Tüddern":"Selfkant - Tüddern"}

def remapping(key,value):
	value=value.encode("utf-8")
	if key=="addr:postcode":
                value=value.replace(" ","")
	elif key=="addr:city":
        	if value in remapCity:
                	value=remapCity[value]
	return value


def shape_element(element):
    node = {}
    nodeCreated = {}
    nodeAddress={}
    if element.tag == "node" or element.tag == "way" :
        for item in element.items():
            if item[0] in CREATED:
                nodeCreated[item[0]]=item[1]
            elif not (item[0]=='lat' or item[0]=='lon' ):
                node[item[0]]=item[1]
        lat=None
        lon=None
        if not element.get("lat")==None:
            lat = float(element.get("lat"))
        if not element.get("lon")==None:
            lon = float(element.get("lon"))
        node["pos"]=[lat,lon]
        for tag in element.iter("tag"):
            kValue=tag.get("k")
            kValueSplitted = kValue.split(":")
            if not re.search(problemchars, kValue):
               if not kValueSplitted[0]=="addr":
                  node[kValue] = remapping(kValue,tag.get("v"))
               elif len(kValueSplitted)==2 and kValueSplitted[0]=="addr":
                  nodeAddress[kValueSplitted[1]]= remapping(kValue,tag.get("v"))
        if len(nodeAddress)>0:
            node["address"]=nodeAddress
        node["created"]=nodeCreated
        node['type']=element.tag
        if element.tag=='way':
            ndA=[]
            for nd in element.iter("nd"):
                kValue=nd.get("ref")
                ndA.append(kValue)
            if len(ndA)>0:
                node["node_refs"]=ndA
        return node
    else:
        return None


def process_map(file_in, pretty = False):
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w",encoding="utf-8") as fo:
        for _, element in ET.iterparse(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
                if pretty:
                    fo.write(json.dumps(el, indent=2)+"\n")
                else:
                    fo.write(json.dumps(el) + "\n")


def runner():
        fileName=sys.argv[1]
        print "Create JSON from XML file " + fileName
        starttime= datetime.datetime.now()
        print "Start: " + str(starttime)
        print ""
        process_map(fileName,True)
        #pprint.pprint(output)
        print ""
        endtime=datetime.datetime.now()
        print "End: " + str(endtime)
        print "Delta: " + str(endtime-starttime)

if __name__ == "__main__":
        if len(sys.argv)!=2:
                print "<script>.py <filename of xml file to analyze>"
                sys.exit(2)
        runner()

