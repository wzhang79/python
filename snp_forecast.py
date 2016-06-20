import datetime
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn
from pandas.io.data import DataReader
from sklearn.qda import QDA
from vectorized_backtest import Strategy,Portfolio
from forecasting_financial_time_series import create_lagged_series

class SNPForecastingStrategy(Strategy):
	def __init__(self,symbol,bars):
		self.symbol=symbol
		self.bars=bars
		self.create_periods()
		self.fit_model()

	def create_periods(self):
		self.start_train=datetime.datetime(2001,1,10)
		self.start_test=datetime.datetime(2005,1,1)
		self.end_period=datetime.datetime(2005,12,31)

	def fit_model(self):
		snpret=create_lagged_series(self.symbol,self.start_train,self.end_period,lags=5)
		X=snpret[['Lag1','Lag2']]
		Y=snpret['Direction']
		X_train=X[X.index<self.start_test]
		Y_train=Y[Y.index<self.start_test]
		self.predictors=X[X.index>=self.start_test]
		self.model=QDA()
		self.model.fit(X_train,Y_train)

	def generate_signals(self):
		signals=pd.DataFrame(index=self.bars.index)
		signals['signal']=0.0
		signals['signal']=self.model.predict(self.predictors)
		signals['signal'][0:5]=0.0
		signals['positions']=signals['signal'].diff()
		return signals

class MarketIntradayPortfolio(Portfolio):
	def __init__(self,symbol,bars,signals,initial_capital=100000.0):
		self.symbol=symbol
		self.bars=bars
		self.signals=signals
		self.initial_capital=float(initial_capital)
		self.positions=self.generate_positions()

	def generate_positions(self):
		positions=pd.DataFrame(index=self.signals.index).fillna(0.0)
		positions[self.symbol]=500*self.signals['signal']
		return positions

	def backtest_portfolio(self):
		portfolio=pd.DataFrame(index=self.positions.index)
		pos_diff=self.positions.diff()
		portfolio['price_diff']=self.bars['Close']-self.bars['Open']
		portfolio['price_diff'][0:5]=0.0
		portfolio['profit']=self.positions[self.symbol]*portfolio['price_diff']
		portfolio['total']=self.initial_capital+portfolio['profit'].cumsum()
		portfolio['return']=portfolio['total'].pct_change()
		return portfolio

if __name__=='__main__':
	start_test=datetime.datetime(2005,1,1)
	end_period=datetime.datetime(2005,12,31)
	bars=DataReader('SPY','yahoo',start_test,end_period)
	snpf=SNPForecastingStrategy('^GSPC',bars)
	signals=snpf.generate_signals()	
	portfolio=MarketIntradayPortfolio('SPY',bars,signals,initial_capital=100000.0)
	returns=portfolio.backtest_portfolio()
	fig=plt.figure()
	#fig.patch.set_facecolor('white')
	ax1=fig.add_subplot(211,ylabel='SPY ETF price in $')
	bars['Close'].plot(ax=ax1,color='r',lw=2.)
	ax2=fig.add_subplot(212,ylabel='Portfolio value in $')
	returns['total'].plot(ax=ax2,lw=2.)
	plt.show()
