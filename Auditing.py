
# coding: utf-8

# #### Open Street Map Project: Suburban Area near Mumbai, India

# This script is intended for auditing the OSM data.
# 
# I used the ElementTree module for parsing the XML data.

# In[1]:

import xml.etree.ElementTree as ET
import pprint


# I used an area of the world around latitude-longitude : 19.2133-73.0467. Since this is a large area, I took a sample for ease of running my code.

# In[2]:

OSM_FILE = "map"
SAMPLE_FILE = "sample.osm"


# In[3]:


k = 5 # Parameter: take every k-th top level element
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
    


# To find out all the tag names and their count in my osm file, I wrote this function :

# In[4]:

def count_tags(filename):
    tags = {}
    for event,elem in ET.iterparse(filename):
        if elem.tag in tags.keys():
            tags[elem.tag] += 1
        else:
            tags[elem.tag] = 1
    return tags


# In[6]:

tags = count_tags(OSM_FILE)
pprint.pprint(tags)


# This tells me that the XML data from Open Street Map has 10 types of tags and it gives me the exact count of each for my chosen area.

# Each 'tag' element has key-value pair.
# Using regular expressions matching operations, I would like to know more about the keys.

# In[8]:

import re
lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

def key_type(element,keys):
    if element.tag == "tag":
        if lower_colon.search(element.attrib["k"]):
            keys["lower_colon"] += 1
        elif problemchars.search(element.attrib["k"]):
            keys["problemchars"] += 1
        elif lower.search(element.attrib["k"]):
            keys["lower"] += 1
        else:
            keys["other"] += 1
    return keys

def process_map(filename):
    keys = {"lower":0, "lower_colon":0, "problemchars":0, "other":0}
    for _,element in ET.iterparse(filename):
        keys = key_type(element, keys)
    return keys

keys = process_map(OSM_FILE)
pprint.pprint(keys)


# This tells me that most of the keys in my file are lowercase, some are lowercase, with a colon, 3 have problem characters in them and a few cannot be classified into any of these categories.

# Many users have contributed to OSM Project. Each user has a unique ID. With the help of this unique ID, I wrote this function that gives a list of the users for any map area.

# In[11]:

def process_users_map(filename):
    users = set()
    for _, element in ET.iterparse(filename):
        if element.get("uid"):
            users.add(element.attrib["uid"])
    return users

users = process_users_map(SAMPLE_FILE)
#pprint.pprint(users)
#len(users)


# I generalized this function :

# In[ ]:

def find_unique(filename, key):
    key_set = set()
    for _, element in ET.iterparse(filename):
        if element.get(key):
            key_set.add(element.attrib[key])
    return key_set


# I can use this function to find all the unique "k"s in my file :

# In[23]:

k_keys = find_unique(SAMPLE_FILE,"k")
#pprint.pprint(k_keys)
#len(k_keys)


# Unique "v" s in my file :

# In[29]:

v_keys = find_unique(SAMPLE_FILE,"v")
#pprint.pprint(v_keys)
#len(v_keys)


# I wrote the following code to check out all the unique "k"-"v" values in the "tag" elements:

# In[32]:

from collections import defaultdict
key_value = defaultdict(set)
for _,element in ET.iterparse(OSM_FILE):
    for tag in element.iter("tag"):
        for k in k_keys:
            if tag.attrib["k"] == k:
                key_value[k].add(tag.attrib["v"])
        
#pprint.pprint(dict(key_value))


# This way I could see all the tag keys and their values. I looked at each key in detail https://taginfo.openstreetmap.org/keys. This gave me a good idea of the available data.

# This key "Golden Park" seems odd. In all of the OSM databases, its been used only here.
# There are other keys too like "maneshi dham","mangeshi dham" that were unique.
