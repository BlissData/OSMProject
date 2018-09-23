
# coding: utf-8

# In[1]:

import sqlite3
import pandas as pd
get_ipython().magic('matplotlib inline')
import matplotlib.pyplot as plt
import seaborn as sns


# In[2]:

db = sqlite3.connect("osm.db")


# Following query shows the list of Restaurants in nodes_tags_db:

# In[42]:

c = db.cursor()
Query2 = '''select value from nodes_tags_db where id in (select id from nodes_tags_db where value="restaurant") and (key="name" or type="name")'''
c.execute(Query2)
rows = c.fetchall()
df = pd.DataFrame(rows, columns = ["RESTAURANTS"])
df.index = df.index + 1
#print (df)


# Following query shows the list of Restaurants in ways_tags_db:

# In[43]:

c = db.cursor()
Query2 = '''select value from ways_tags_db where id in (select id from ways_tags_db where value="restaurant") and (key="name" or type="name")'''
c.execute(Query2)
rows = c.fetchall()
df = pd.DataFrame(rows, columns = ["RESTAURANTS"])
df.index = df.index + 1
#print (df)


# Following query gives a list of postcodes in the data and their corresponding occurrences. I have also plotted a barplot.

# In[5]:

c = db.cursor()
Query = 'select tags.value,count(*) as n from (select * from nodes_tags_db union all select * from ways_tags_db)tags where (tags.key="postcode" or tags.key="postal_code") group by tags.value order by n desc'
c.execute(Query)
rows = c.fetchall()
df = pd.DataFrame(rows,columns=["postcode","count"])
df.loc[11]=[400076,4]
df = df.drop(df.index[[19,23,27,28,29]])
#print (df)
labels = df["postcode"]
sns.barplot(df["postcode"],df["count"]).set_xticklabels(labels,rotation=30)


# Following query gives the number of nodes in the data :

# In[6]:

c = db.cursor()
Q = 'select count(*) from nodes_db'
c.execute(Q)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# Following query gives the number of ways in the data :

# In[7]:

c = db.cursor()
Q = 'select count(*) from ways_db'
c.execute(Q)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# Following query shows all the distinct keys and their number of occurences in nodes_tags_db:

# In[8]:

Query = 'select key,count(*) as n from nodes_tags_db group by key order by n desc'
c.execute(Query)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# Following query shows all the distinct key-types in nodes_tags_db:

# In[9]:

Query = 'select distinct type from nodes_tags_db'
c.execute(Query)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# Following query shows all rows with type "name" in nodes_tags_db:

# In[10]:

Q = 'select * from nodes_tags_db where type="name"'
c.execute(Q)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print(df)


# Following queries show all the schools in nodes_tags_db and ways_tags_db:

# In[12]:

c = db.cursor()
Query2 = '''select distinct value from nodes_tags_db where id in (select id from nodes_tags_db where value="school") and (key="name" or type="name")'''
c.execute(Query2)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# In[13]:

c = db.cursor()
Query2 = '''select distinct value from ways_tags_db where id in (select id from ways_tags_db where value="school") and (key="name" or type="name")'''
c.execute(Query2)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# Following queries show all the shops in nodes_tags_db and ways_tags_db:

# In[14]:

c = db.cursor()
Query = 'select value from nodes_tags_db where id in (select id from nodes_tags_db where key="shop") and (key="name" or type="name")'
c.execute(Query)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# In[15]:

c = db.cursor()
Query = 'select value from ways_tags_db where id in (select id from ways_tags_db where key="shop") and (key="name" or type="name")'
c.execute(Query)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# Following query shows number of occurrences of different natural landscapes in ways_tags_db:  

# In[16]:

c = db.cursor()
Query = 'select value,count(*) as n from ways_tags_db where key=="natural" group by value'
c.execute(Query)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# Following queries show all the hospitals in nodes_tags_db and ways_tags_db:

# In[17]:

c = db.cursor()
Query1 = 'select value from nodes_tags_db where id in (select id from nodes_tags_db where value="hospital") and (key="name" or type="name")'
c.execute(Query1)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# In[18]:

c = db.cursor()
Query1 = 'select value from ways_tags_db where id in (select id from ways_tags_db where value="hospital") and (key="name" or type="name")'
c.execute(Query1)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# Following queries show all the movie theatres in nodes_tags_db and ways_tags_db:

# In[19]:

c = db.cursor()
Query = 'select value from nodes_tags_db where id in(select id from nodes_tags_db where value="cinema") and (key="name" or type="name")'
c.execute(Query)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# In[20]:

c = db.cursor()
Query = 'select value from ways_tags_db where id in(select id from ways_tags_db where value="cinema") and (key="name" or type="name")'
c.execute(Query)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# Following query shows users and their contribution in descending order in nodes_db:

# In[21]:

c = db.cursor()
Query = 'select user,count(*) as n from nodes_db group by uid order by n desc'
c.execute(Query)
rows = c.fetchall()
df1 = pd.DataFrame(rows, columns=["USER","CONTRIBUTION"])
df1.index = df1.index + 1
#print (df1)
#len (df1)


# Following query shows number of unique users in nodes_db:

# In[22]:

c = db.cursor()
Query = 'select uid,count(*) as n from nodes_db group by uid order by n desc'
c.execute(Query)
rows = c.fetchall()
df1 = pd.DataFrame(rows)
#print (df1)
len (df1)


# Following query shows number of unique users in ways_db:

# In[24]:

c = db.cursor()
Query = 'select uid,count(*) as n from ways_db group by uid order by n desc'
c.execute(Query)
rows = c.fetchall()
df2= pd.DataFrame(rows)
#print (df)


# Following query shows unique users in ways_db combined with nodes_db, their contribution, their total contribution. It also plots a graph of unique users vs their contribution.  :

# In[25]:

c = db.cursor()
Query = 'select tags.uid,count(*) as n from (select uid from nodes_db union all select uid from ways_db)tags group by tags.uid order by n desc'
c.execute(Query)
rows = c.fetchall()
df= pd.DataFrame(rows,columns=["uid","count"])
print('Total contribution by all users is', sum(df["count"]))
#print (df)
print ('Number of unique users is',len (df))
plt.plot(df["uid"],df["count"],"ro")


# Following query shows number of unique users who contributed only once :

# In[26]:

c = db.cursor()
Query = 'select count(*) from (select tags.uid,count(*) as n from (select uid from nodes_db union all select uid from ways_db)tags group by tags.uid having n=1)'
c.execute(Query)
rows = c.fetchall()
df= pd.DataFrame(rows)
print (df)


# Following 2 queries are to confirm that the 2 postcodes I came across earlier do not belong to this area of the map.

# In[27]:

Q = 'select * from nodes_tags_db where id = (select id from nodes_tags_db where value = 560092)'
c.execute(Q)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print(df)


# In[28]:

Q = 'select * from ways_tags_db where id = (select id from ways_tags_db where value = 560103)'
c.execute(Q)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print(df)


# Following query shows number of levels in buildings and their occurrences:

# In[29]:

c = db.cursor()
Query = 'select tags.*,count(*) as n from (select * from nodes_tags_db union all select * from ways_tags_db)tags where tags.key="levels" group by tags.value order by n desc'
c.execute(Query)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# Following query shows number of nodes in each way in ways_nodes_db:

# In[30]:

c = db.cursor()
Query ='select id,count(*) from ways_nodes_db group by id order by count(*) desc limit 10'
c.execute(Query)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# Following query shows, what the ways represent, for which the number of nodes per way is large. For example, the longest way in this map is a "river". 

# In[57]:

c = db.cursor()
Query ='select id,key,value from ways_tags_db where id in (select id from ways_nodes_db group by id order by count(*) desc limit 15)'
c.execute(Query)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# Following query can be used to find number of restaurants, shops, schools, etc. :

# In[58]:

Q = 'select count(*) from (select * from nodes_tags_db union all select * from ways_tags_db)tags where tags.value="school"'
c.execute(Q)
rows = c.fetchall()
df = pd.DataFrame(rows)
#print (df)


# In[59]:

db.close()


# In[ ]:



