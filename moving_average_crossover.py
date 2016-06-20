import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pandas.io.data import DataReader
from vectorized_backtest import Strategy,Portfolio

class MovingAverageCrossStrategy(Strategy):
	def __init__(self,symbol,bars,short_window=100,long_window=400):
		self.symbol=symbol
		self.bars=bars
		self.short_window=short_window
		self.long_window=long_window

	def generate_signals(self):
		signals=pd.DataFrame(0.0,index=self.bars.index,columns=['signal'])
		signals['short_ma']=pd.rolling_mean(self.bars['Adj Close'],self.short_window,min_periods=1)
		signals['long_ma']=pd.rolling_mean(self.bars['Adj Close'],self.long_window,min_periods=1)
		signals['signal'][self.short_window:]=np.where(signals['short_ma'][self.short_window:]>signals['long_ma'][self.short_window:],1.0,0.0)
		signals['positions']=signals['signal'].diff()
		return signals


class MarketOnClosePortfolio(Portfolio):
	def __init__(self,symbol,bars,signals,initial_capital=100000.0):
		self.symbol=symbol
		self.bars=bars
		self.signals=signals
		self.initial_capital=float(initial_capital)
		self.positions=self.generate_positions()

	def generate_positions(self):
		positions=pd.DataFrame(index=signals.index).fillna(0.0)
		positions[self.symbol]=100*signals['positions']
		return positions

	def backtest_portfolio(self):
		portfolio=pd.DataFrame(index=self.positions.index).fillna(0.0)
		portfolio['holdings']=self.positions.cumsum().mul(self.bars['Adj Close'],axis=0)
		portfolio['cash']=self.initial_capital-(self.positions.mul(self.bars['Adj Close'],axis=0).cumsum())
		portfolio['total']=portfolio['cash']+portfolio['holdings']
		portfolio['returns']=portfolio['total'].pct_change()
		return portfolio

class Performance():
	def __init__(self,returns,bars,signals):
		self.returns=returns
		self.bars=bars
		self.signals=signals
	def perform(self):
		fig=plt.figure()
		fig.patch.set_facecolor('white')
		ax1=fig.add_subplot(211,ylabel='Price in $')
		self.bars['Adj Close'].plot(ax=ax1,color='r',lw=2.)
		self.signals[['short_ma','long_ma']].plot(ax=ax1,lw=2.)
		ax1.plot(self.signals.ix[self.signals.positions==1.0].index,self.signals.short_ma[self.signals.positions==1.0],'^',markersize=10,color='m')
		ax1.plot(self.signals.ix[self.signals.positions==-1.0].index,self.signals.short_ma[self.signals.positions==-1.0],'v',markersize=10,color='k')

		ax2=fig.add_subplot(212,ylabel='Portfolio value in $')
		self.returns['total'].plot(ax=ax2,lw=2.)
		ax2.plot(self.returns.ix[self.signals.positions==1.0].index,self.returns.total[self.signals.positions==1.0],'^',markersize=10,color='m')
		ax2.plot(self.returns.ix[self.signals.positions==-1.0].index,self.returns.total[self.signals.positions==-1.0],'v',markersize=10,color='k')
		plt.show()
		

		

if __name__=="__main__":
	symbol='XOM'
	bars=DataReader(symbol,"yahoo",datetime.datetime(2012,1,1),datetime.datetime(2015,1,1))
	macs=MovingAverageCrossStrategy(symbol,bars)
	signals=macs.generate_signals()
	portfolio=MarketOnClosePortfolio(symbol,bars,signals)
	returns=portfolio.backtest_portfolio()
	perf=Performance(returns,bars,signals)
	perf.perform()
