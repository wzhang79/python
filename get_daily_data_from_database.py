import sys
import pandas as pd
import pandas.io.sql as psql
import MySQLdb as mdb
import matplotlib.pyplot as plt
from numpy import *
from pandas import DataFrame
import itertools as it

db_host='localhost'
db_user='sec_user'
db_pass='Yutian630403'
db_name='securities_master'
con=mdb.connect(db_host,db_user,db_pass,db_name)

def get_daily_data_from_db_new(ticker,start_date, end_date):
	sql="""SELECT dp.price_date,open_price,high_price,low_price,close_price,volume,adj_close_price
		FROM symbol AS sym
		INNER JOIN daily_price AS dp
		ON dp.symbol_id=sym.id
		WHERE sym.ticker='%s'
		AND dp.price_date>='%s'
		AND dp.price_date<='%s'
		ORDER BY dp.price_date ASC;""" % (ticker,start_date,end_date)
	data=psql.read_sql(sql,con=con,index_col='price_date')
	return data

def get_daily_data_from_db(ticker,data_type,start_date,end_date):
	data_type='dp.'+data_type
	sql="""SELECT dp.price_date,%s
		FROM symbol AS sym
		INNER JOIN daily_price AS dp
		ON dp.symbol_id=sym.id
		WHERE sym.ticker='%s'
		AND dp.price_date>='%s'
		AND dp.price_date<='%s'
		ORDER BY dp.price_date ASC;""" % (data_type,ticker,start_date,end_date)
	data=psql.read_sql(sql,con=con,index_col='price_date')
	return data

def simulate(start_date,end_date,tickers,initial_allocation):
	adj_close_price={ticker:get_daily_data_from_db(ticker,'adj_close_price',start_date,end_date) for ticker in tickers}
	adj_close_price_comb=pd.concat(adj_close_price,axis=1)
	ret=adj_close_price_comb.pct_change()
	ret_port=(ret*initial_allocation).sum(axis=1)
	ret_avg_port=ret_port.mean()
	vol_port=ret_port.std()
	cum_ret_port=(1+ret_port).cumprod()
	rf=0
	sharp_ratio_port=sqrt(252)*(ret_avg_port-rf)/vol_port
	return(sharp_ratio_port)

def optimize(start_date,end_date,tickers):
	adj_close_price={ticker:get_daily_data_from_db(ticker,'adj_close_price',start_date,end_date) for ticker in tickers}
	adj_close_price_comb=pd.concat(adj_close_price,axis=1)
	ret=adj_close_price_comb.pct_change()
	ret_avg=mat(ret.mean().as_matrix()).T
	rf=0
	n=len(tickers)
	cov=mat(ret.cov().as_matrix())
	cov_inv=linalg.inv(cov)
	A=(ret_avg-rf).T*cov_inv*(ret_avg-rf)
	lmd=-1/A.item(0)
	w=-lmd*cov_inv*(ret_avg-rf)
	x=w/w.sum()
	return x.flatten().tolist()[0]

def get_snp_500_tickers():
	sql="""SELECT ticker FROM symbol;"""
	data=psql.read_sql(sql,con=con,columns='ticker')
	return data['ticker'].tolist()

def optimize_N(start_date,end_date,tickers,N):
	combinations=it.combinations(tickers,N)	

if __name__=='__main__':
#	start_date=sys.argv[1]
#	end_date=sys.argv[2]
#	tickers=[]
#	for arg in sys.argv[3:]:
#		tickers.append(arg)
#	initial_allocation=[1.0/len(tickers)]*len(tickers)
	start_date='2013-1-1'
	end_date='2015-1-1'
#	tickers=['AAPL','XOM','MSFT']
#	initial_allocation=[0.2,0.5,0.3]
#	sharp_ratio_1=simulate(start_date,end_date,tickers,initial_allocation)
#	optimized_allocation=optimize(start_date,end_date,tickers)
#	sharp_ratio_2=simulate(start_date,end_date,tickers,optimized_allocation)
#	print(initial_allocation,sharp_ratio_1)
#	print(optimized_allocation,sharp_ratio_2)
	tickers=get_snp_500_tickers()
	optimize_N(start_date,end_date,tickers,50)
