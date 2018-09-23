
# coding: utf-8

# #### Open Street Map Project: Suburban Area near Mumbai, India

# This script is intended for cleaning the OSM data partially. I take my OSM file, correct some areas of it, validate against a validator using Cerberus, and then create csv files for further use.

# I used the ElementTree module for parsing the XML data.

# In[9]:

import xml.etree.ElementTree as ET
import pprint
from collections import defaultdict


# I used an area of the world around latitude-longitude : 19.2133-73.0467.
# Since this is a large area, I took a sample for ease of running my code.

# In[2]:

OSM_FILE = "map"
SAMPLE_FILE = "sample.osm"


# Following code takes the sample :

# In[3]:


k = 5 #Parameter: take every k-th top level element
def get_element(osm_file, tags=('node','way','relation')):
    #yield element if it is the right type of tag
    context = ET.iterparse(osm_file, events=('start','end'))
    _,root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()
            
with open(SAMPLE_FILE, 'w', encoding="UTF-8") as output:
    output.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    output.write('<osm version="0.6" generator="Overpass API">\n')
    
    #write every k-th top level element
    for i,element in enumerate(get_element(OSM_FILE)):
        if i%k == 0:
            output.write(ET.tostring(element, encoding='unicode'))
    output.write('</osm>')
    


# In[4]:

import csv
import codecs
import cerberus
import schema
import re

NODES_PATH = "nodes.csv"
NODES_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAYS_NODES_PATH = "ways_nodes.csv"
WAYS_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id','user','uid','version','changeset','timestamp']
WAY_TAGS_FIELDS = ['id','key','value','type']
WAY_NODES_FIELDS = ['id','node_id','position']


# In[5]:

def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS,
                 problem_chars=PROBLEMCHARS, default_tag_type='regular'):
    
    #found this one tag inconsistent while auditing, so converted it:
    for tag in element.iter("tag"):
        if tag.attrib["k"] == "addr:place":
            tag.attrib["k"] = tag.attrib["k"].replace("addr:place","addr:city")
            tag.attrib["v"] = tag.attrib["v"].replace("Bhandup West","Bhandup (West)")

    # Data Harmonization : tried to bring uniformity in the street names. There were still some
    # more that I could not correct because I did not want to lose any data.
    street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
    expected = ["Road","Marg","Circle","Chowk","Highway","Path","Lane"]
    mapping = {"Rd":"Road","rd":"Road","ROAD":"Road","ROad":"Road","marg":"Marg","road":"Road",
              "road)":"Road","chowk":"Chowk"}

    def audit_street_type(street_types, street_name):
        m = street_type_re.search(street_name)
        if m:
            street_type = m.group()
            if street_type not in expected:
                street_types[street_type].add(street_name)
    
    def audit(tag):
        street_types = defaultdict(set)
        audit_street_type(street_types, tag.attrib['v'])
        return street_types

    def update_name(name, mapping):
        st_types = audit(tag)
        for k,n in st_types.items():
            if name in n:
                key_name = k
                for ke,na in mapping.items():
                    if ke == key_name:
                        correct_key_name = na
                        name = name.replace(key_name, correct_key_name)
            else:
                name = name
        return name

    # Here I apply above 3 functions to correct the street names:
    for tag in element.iter("tag"):
        if tag.attrib["k"] == "addr:street":
            tag.attrib["v"] = update_name(tag.attrib["v"], mapping)
    

    # While auditing, I saw inconsistencies in the City names, which I corrected as follows:
    mapping_city = {"BANGALORE":"Bangalore", "DIva":"Diva", "Dombivli West":"Dombivli (West)",
                   "Kanjur Marg (E)":"Kanjurmarg (East)", "MULUND (WEST)":"Mulund (West)",
                   "MUMBAI":"Mumbai", "Mulind (East)":"Mulund (East)","Mulond (West)":"Mulund (West)",
                   "Mulund (Weat)":"Mulund (West)", "THANE":"Thane", "Thane (west)":"Thane (West)",
                   "Thane West":"Thane (West)", "banglore":"Bangalore","bhandup":"Bhandup",
                   "bhiwandi":"Bhiwandi","kalwa":"Kalwa","Thankurli(E),Dist Thane":"Thakurli (East)",
                   "mumbai":"Mumbai","thane":"Thane","Mulund(West)":"Mulund (West)"}
    for tag in element.iter("tag"):
        if tag.attrib["k"] == "addr:city":
            for v,V in mapping_city.items():
                if tag.attrib["v"] == v:
                    tag.attrib["v"] = tag.attrib["v"].replace(v,V)
            


    # In order to correct some inconsistencies in the postcode and phone, I found myself 
    # repeating certain steps. So I wrote the following function for efficiency : 
    def replace_value(tag,sp):
        tag.attrib["v"] = tag.attrib["v"].replace(tag.attrib["v"], "".join(tag.attrib["v"].split(sp)))
        return tag.attrib["v"]

    # Applied the function to correct some postcodes:
    for tag in element.iter("tag"):
        if tag.attrib["k"] == "addr:postcode":
            x = len(tag.attrib["v"])
            if x == 7:
                tag.attrib["v"] = replace_value(tag," ")

    # Applied the function to correct some phone numbers:
    for tag in element.iter("tag"):
        if tag.attrib["k"] == "phone":
            gaps = [" ","-"]
            for gap in gaps:
                tag.attrib["v"] = replace_value(tag,gap)
    
    
    # After all the corrections, it is time to sort all the elements into nodes, ways, their
    # tags, and nodes in the ways.
    
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags_list = []
    
    # Following function assists the sorting process.
    # It decides how the "tag" elements will be stored in the csv files.
    def build_tag_list(elem):
        tag_list = []
        for tag in elem.iter("tag"):
            if problem_chars.search(tag.attrib["k"]):
                continue
            if LOWER_COLON.search(tag.attrib["k"]):
                tags_dict = {}
                tags_dict["id"] = elem.attrib["id"]
                tags_dict["type"],tags_dict["key"] = tag.attrib["k"].split(":",1)
                tags_dict["value"] = tag.attrib["v"]
                tag_list.append(tags_dict)
            else:
                tags_dict = {}
                tags_dict["id"] = elem.attrib["id"]
                tags_dict["key"] = tag.attrib["k"]
                tags_dict["value"] = tag.attrib["v"]
                tags_dict["type"] = default_tag_type
                tag_list.append(tags_dict)
        return tag_list
    
    # Here each element gets sorted :
    if element.tag == 'node':
        tags_list = build_tag_list(element)
        for field in node_attr_fields:
            node_attribs[field] = element.attrib[field]
        return {'node':node_attribs, 'node_tags':tags_list}
    elif element.tag == 'way':
        tags_list = build_tag_list(element)
        for field in way_attr_fields:
            way_attribs[field] = element.attrib[field]
        pos = 0
        for tag in element.iter("nd"):
            way_dict = {}
            way_dict["id"] = element.attrib["id"]
            way_dict["node_id"] = tag.attrib["ref"]
            way_dict["position"] = pos
            way_nodes.append(way_dict)
            pos += 1
        return {'way':way_attribs, 'way_nodes':way_nodes, 'way_tags':tags_list}


# In[6]:

# Following function is called at the time of validation:
def validate_element(element, validator, schema=SCHEMA):
    if validator.validate(element,schema) is not True:
        field,errors = next(iter(validator.errors.items()))
        #field,errors = next(enumerate(validator.errors))
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)
        
        raise Exception(message_string.format(field,error_string))
        

# Defining a CSV writer for writing rows to a CSV file:
class UnicodeDictWriter(csv.DictWriter, object):
    
    def writerow(self,row):
        super(UnicodeDictWriter, self).writerow({
            k:v for k,v in row.items()
        })
        
    def writerows(self,rows):
        for row in rows:
            self.writerow(row)
    


# In[7]:

# The following function opens the csv files using codecs module, and writes the elements as 
# rows if the validator validates them. 
def process_map(file_in, validate):
    
    with codecs.open(NODES_PATH,'w',encoding='utf-8') as nodes_file,          codecs.open(NODES_TAGS_PATH,'w',encoding='utf-8') as nodes_tags_file,          codecs.open(WAYS_PATH,'w',encoding='utf-8') as ways_file,          codecs.open(WAYS_NODES_PATH,'w',encoding='utf-8') as way_nodes_file,          codecs.open(WAYS_TAGS_PATH,'w',encoding='utf-8') as way_tags_file:
                
        nodes_writer = UnicodeDictWriter(nodes_file,NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file,NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file,WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file,WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file,WAY_TAGS_FIELDS)
        
        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()
        
        validator = cerberus.Validator()
        
        for element in get_element(file_in, tags=('node','way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)
                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])
                    
                    


# In[11]:

if __name__ == '__main__':
    process_map(OSM_FILE, validate=True)

