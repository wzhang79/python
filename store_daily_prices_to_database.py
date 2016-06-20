import MySQLdb as mdb
import datetime
import pandas as pd
from pandas import Series, DataFrame
import pandas.io.data as web
from warnings import filterwarnings

filterwarnings('ignore',category=mdb.Warning)
db_host = 'localhost'
db_user = 'sec_user'
db_pass = 'Yutian630403'
db_name = 'securities_master'
con = mdb.connect(db_host, db_user, db_pass, db_name)

def obtain_list_of_db_tickers():
	with con:
		cur=con.cursor()
		cur.execute("SELECT id,ticker FROM symbol")
		data=cur.fetchall()
		tickers=[(d[0],d[1]) for d in data]
		return tickers

def get_daily_data_yahoo(tickers,start_date='1/1/2010',end_date='5/1/2015'):
	daily_data={}
	for ticker in tickers:
		try:
			daily_data[ticker[0]]=web.get_data_yahoo(ticker[1],start_date,end_date)
		except:
			print("cannot download %s." % ticker[1])
	return daily_data

def insert_daily_data_into_db(data_vendor_id, daily_data):
	now=datetime.datetime.utcnow()
	column_str="""data_vendor_id, symbol_id, price_date, created_date, 
	          last_updated_date, open_price, high_price, low_price, 
		            close_price, volume, adj_close_price"""
	insert_str=("%s, " * 11)[:-2]
	final_str="INSERT INTO daily_price (%s) VALUES (%s)" % (column_str,insert_str)
	with con:
		cur=con.cursor()
		cur.execute("TRUNCATE TABLE daily_price")
		for k,v in daily_data.iteritems():
			tick_data=[(data_vendor_id,k,index,now,now,row.values[0],
				row.values[1],row.values[2],row.values[3],row.values[4],row.values[5]) for index,row in v.iterrows()]
			cur.executemany(final_str,tick_data)
			print("add symbol_id %s" % k)

if __name__=="__main__":
	tickers=obtain_list_of_db_tickers()
	daily_data=get_daily_data_yahoo(tickers)
	insert_data=insert_daily_data_into_db(1,daily_data)
