import unicodedata
import sqlite3
connection=sqlite3.connect("/Users/weileizhang/Desktop/testDB.db")
cursor=connection.cursor()
cursor.execute("select * from finance")
data=[]
for row in cursor:
	line=[]
	for k in row:
		if(isinstance(k,unicode)):
			k=k.encode('ascii','ignore')
		line.append(k)
	data.append(line)
