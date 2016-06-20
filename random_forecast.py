import numpy as np
import pandas as pd
from get_daily_data_from_database import get_daily_data_from_db
from vectorized_backtest import Strategy, Portfolio

class RandomForecastingStrategy(Strategy):
	def __init__(self,symbol,bars):
		self.symbol=symbol
		self.bars=bars

	def generate_signals(self):
		signals=pd.DataFrame(index=self.bars.index)
		signals['signal']=np.random.randint(3,size=len(signals))-1
		signals['signal'][0:5]=0.0
		return signals

class MarketOnOpenPortfolio(Portfolio):
	def __init__(self,symbol,bars,signals,initial_capital=100000.0):
		self.symbol=symbol
		self.bars=bars
		self.signals=signals
		self.initial_capital=float(initial_capital)
		self.positions=self.generate_positions()

	def generate_positions(self):
		positions=pd.DataFrame(index=self.signals.index)
		positions[self.symbol]=100*self.signals['signal']
		return positions

	def backtest_portfolio(self):
		portfolio=pd.DataFrame(index=self.signals.index)
		portfolio['positions']=self.positions
		portfolio['open_price']=self.bars['open_price']
		portfolio['holdings']=self.positions.cumsum()*self.bars['open_price']
		portfolio['cash']=self.initial_capital-(self.positions*self.bars['open_price']).cumsum()
		portfolio['total']=portfolio['cash']+portfolio['holdings']
		portfolio['returns']=portfolio['total'].pct_change()
		return portfolio

if __name__=="__main__":
	start_date='2012-1-1'
	end_date='2015-1-1'
	ticker='AAPL'
	bars=get_daily_data_from_db(ticker,'open_price',start_date,end_date)
	rfs=RandomForecastingStrategy(ticker,bars)
	signals=rfs.generate_signals()
	portfolio=MarketOnOpenPortfolio(ticker,bars,signals,initial_capital=100000.0)
	returns=portfolio.backtest_portfolio()
	print(returns)
