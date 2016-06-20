import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import operator
from get_daily_data_from_database import get_daily_data_from_db, get_snp_500_tickers
from vectorized_backtest import Strategy, Portfolio, Performance

class EventDrivenStrategy(Strategy):
	def __init__(self,tickers,bars):
		self.tickers=tickers
		self.bars=bars

	def generate_signals(self):
		market_price=self.bars['SPY']
		self.bars=self.bars.drop('SPY',axis=1)
		returns_portfolio=self.bars.pct_change()
		returns_market=market_price.pct_change()
		signals=pd.DataFrame(0,index=bars.index,columns=bars.columns)
		result={index:[] for index in range(-5,5)}
		for index, value in returns_market.iterrows():
			if(value['adj_close_price']>=0.01):
				for ticker in returns_portfolio.ix[index].index:
					if(returns_portfolio[ticker].ix[index]<=0):
						signals[ticker].ix[index]=1
		for i in range(signals.shape[0]):
			for j in range(signals.shape[1]):
				if(signals.iloc[i,j]==1):
					for k in range(-5,5):
						result[k].append(returns_portfolio.iloc[i+k,j])
		result_avg={k:np.array(result[k]).mean() for k in result.keys()}
		result_avg=sorted(result_avg.items(),key=operator.itemgetter(0))
		result_x=[x[0] for x in result_avg]
		result_y=[x[1] for x in result_avg]
		plt.clf()
		plt.plot(result_x,result_y)
		plt.show()
	
class MarketOnClosePortfolio(Portfolio):
	def __init__(self,strategy,initial_capital=100000.0):
		self.symbol=strategy.tickers
		self.bars=strategy.bars
		self.signals=strategy.signals
		self.initial_capital=float(initial_capital)
		self.positions=self.generate_positions()

	def generate_positions(self):
		positions=self.signals
		return positions

	def backtest_portfolio(self):
		portfolio=pd.DataFrame(index=self.signals.index)
		portfolio['operating']=(self.bars*self.positions).sum(axis=1)
		portfolio['cash']=self.initial_capital-portfolio['operating'].cumsum()
		portfolio['holdings']=(self.positions.cumsum()*self.bars).sum(axis=1)
		portfolio['total']=portfolio['cash']+portfolio['holdings']
		portfolio['returns']=portfolio['total'].pct_change()
		return portfolio



def get_data_from_csv(filename):
	data=pd.read_csv(filename,index_col=False,header=None, names=('year','month','date','ticker','buy_sell','units'),converters={'year':np.int32,'month':np.int32,'date':np.int32,'ticker':str,'buy_sell':str,'units':np.int64})
	data['datetime']=[datetime.datetime(x[0],x[1],x[2]) for x in zip(data['year'],data['month'],data['date'])]
	data=data.set_index('datetime')
	data=data.drop(['year','month','date'],axis=1)
	tickers=data['ticker'].unique()
	start_date=data.index.min().strftime('%Y-%m-%d')
	end_date=data.index.max().strftime('%Y-%m-%d')
	daily_data={ticker:get_daily_data_from_db(ticker,'adj_close_price',start_date,end_date) for ticker in tickers}
	bars=pd.concat(daily_data,axis=1)
	for col in bars.columns:
		bars[col]=bars[col].fillna(0)
	signals=pd.DataFrame(0,index=bars.index,columns=bars.columns)
	for index,value in data.iterrows():
		ticker=value['ticker']
		unit=value['units']
		if(value['buy_sell']=='Buy'):
			signals[ticker].ix[index]=unit
		else:
			signals[ticker].ix[index]=-unit
	return tickers,bars,signals

if __name__=='__main__':
	#tickers=get_snp_500_tickers()
	tickers=['AAPL','MSFT','SPY']
	start_date='2010-1-1'
	end_date='2015-1-1'
	daily_data={ticker:get_daily_data_from_db(ticker,'adj_close_price',start_date,end_date) for ticker in tickers}
	bars=pd.concat(daily_data,axis=1)
	for col in bars.columns:
		bars[col]=bars[col].fillna(0)
	eds=EventDrivenStrategy(tickers,bars)
	eds.generate_signals()
#	portfolio=MarketOnClosePortfolio(eds,10000000)
#	returns=portfolio.backtest_portfolio()
#	performance=Performance(returns)
#	cumret,sharp_ratio=performance.generate_performance(rf=0)
#	print(cumret)
#	print(sharp_ratio)
