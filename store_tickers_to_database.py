from lxml import html
import requests
import MySQLdb as mdb
import datetime
import pandas as pd
from pandas import Series, DataFrame
import pandas.io.data as web


def get_symbols():
	now=datetime.datetime.utcnow()

	page=requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
	tree=html.fromstring(page.text)
	table=tree.xpath('//table')[0]
	symbols_list=table.xpath('.//tr')[1:]
	symbols=[]
	for symbol in symbols_list:
		tds=symbol.getchildren()
		sd={'ticker':tds[0].getchildren()[0].text,
			'name':tds[1].getchildren()[0].text,
			'sector':tds[3].text}
		symbols.append((sd['ticker'],'stock',sd['name'],
				sd['sector'],'USD',now,now))
	symbols.append(('SPY','stock','S&P500_ETF','index','USD',now,now))
	return symbols

def insert_snp500_symbols(symbols):
	db_host='localhost'
	db_user='sec_user'
	db_pass='Yutian630403'
	db_name='securities_master'
	con=mdb.connect(host=db_host,user=db_user,passwd=db_pass,db=db_name)

	column_str="ticker,instrument,name,sector,currency,created_date,last_updated_date"
	insert_str=("%s, " * 7)[:-2]
	final_str = "INSERT INTO symbol (%s) VALUES (%s)" % (column_str,insert_str)
	with con:
		cur=con.cursor()
		cur.execute("truncate table symbol")
		cur.executemany(final_str, symbols)

def get_data(symbols):
	all_data={}
	for ticker in symbols:
		try:
			all_data[ticker]=web.get_data_yahoo(ticker,'1/1/2015','2/1/2015')
		except:
			print("can not find ", ticker)

	price=DataFrame({tic:data['Adj Close'] for tic, data in all_data.iteritems()})
	volume=DataFrame({tic:data['Volume'] for tic, data in all_data.iteritems()})
	return price,volume

if __name__=='__main__':
	symbols=get_symbols()
	insert_snp500_symbols(symbols)
