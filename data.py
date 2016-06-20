import datetime
import os, os.path
import pandas as pd
from abc import ABCMeta,abstractmethod
from event import MarketEvent
from get_daily_data_from_database import get_daily_data_from_db_new

class DataHandler(object):
	__metaclass__=ABCMeta

	@abstractmethod
	def get_latest_bars(self,symbol,N=1):
		raise NotImplementedError("Should implement get_latest_bars()")

	@abstractmethod
	def update_bars(self):
		raise NoeImplementedError("Should implement update_bars()")

class HistoricCSVDataHandler(DataHandler):
	def __init__(self,events,csv_dir,symbol_list,start_date,end_date):
		self.events=events
		self.csv_dir=csv_dir
		self.symbol_list=symbol_list
		self.start_date=start_date
		self.end_date=end_date
		self.symbol_data={}
		self.latest_symbol_data={}
		self.continue_backtest=True

		self._open_convert_csv_files()

	def _open_convert_csv_files(self):
		comb_index=None
		for s in self.symbol_list:
			self.symbol_data[s]=pd.io.parsers.read_csv(os.path.join(self.csv_dir,'%s.csv' % s),header=0,index_col=0,names=['datetime','open','high','low','close','volume','adj_close'],parse_dates=True)
			if comb_index is None:
				comb_index=self.symbol_data[s].index
			else:
				comb_index=comb_index.union(self.symbol_data[s].index)
			self.latest_symbol_data[s]=[]
		
		comb_index=comb_index[(comb_index>=self.start_date) * (comb_index<=self.end_date)]
		for s in self.symbol_list:
			self.symbol_data[s]=self.symbol_data[s].reindex(index=comb_index).fillna(0.0).iterrows()
		
	
	def _get_new_bar(self,symbol):
		for b in self.symbol_data[symbol]:
			yield tuple([symbol,b[0],b[1][0],b[1][1],b[1][2],b[1][3],b[1][4],b[1][5]])

	def get_latest_bars(self,symbol,N=1):
		try:
			bars_list=self.latest_symbol_data[symbol]
		except KeyError:
			print("That symbol is not available in the historical data set.")
		else:
			return bars_list[-N:]
	
	def update_bars(self):
		for s in self.symbol_list:
			try:
				bar=self._get_new_bar(s).next()
			except StopIteration:
				self.continue_backtest=False
			else:
				if bar is not None:
					self.latest_symbol_data[s].append(bar)
		self.events.put(MarketEvent())

class DataBaseDataHandler(DataHandler):
	def __init__(self,events,symbol_list,start_date,end_date):
		self.events=events
		self.symbol_list=symbol_list
		self.start_date=start_date
		self.end_date=end_date
		self.symbol_data={}
		self.latest_symbol_data={}
		self.continue_backtest=True
		self._get_data_from_db()

	def _get_data_from_db(self):
		comb_index=None
		for s in self.symbol_list:
			self.symbol_data[s]=get_daily_data_from_db_new(s,self.start_date,self.end_date)
			if comb_index is None: 
				comb_index=self.symbol_data[s].index
			else:
				comb_index=comb_index.union(self.symbol_data[s].index)
			self.latest_symbol_data[s]=[]
		comb_index=comb_index[(comb_index>=self.start_date)*(comb_index<=self.end_date)]
		for s in self.symbol_list:
			self.symbol_data[s]=self.symbol_data[s].reindex(index=comb_index).fillna(0.0).iterrows()
	def _get_new_bar(self,symbol):
		for b in self.symbol_data[symbol]:
			yield tuple([symbol,b[0],b[1][0],b[1][1],b[1][2],b[1][3],b[1][4],b[1][5]])

	def get_latest_bars(self,symbol,N=1):
		try:
			bars_list=self.latest_symbol_data[symbol]
		except KeyError:
			print("That symbol is not available in the historical data set.")
		else:
			return bars_list[-N:]
	
	def get_all_bars(self,symbol):
		try:
			bars_list=self.latest_symbol_data[symbol]
		except KeyError:
			print("That symbol is not available in the historical data set.")
		else:
			return bars_list

	def update_bars(self):
		for s in self.symbol_list:
			try:
				bar=self._get_new_bar(s).next()
			except StopIteration:
				self.continue_backtest=False
			else:
				if bar is not None:
					self.latest_symbol_data[s].append(bar)
		self.events.put(MarketEvent())

	def get_data_number(self,symbol):
		return len(self.latest_symbol_data[symbol])
