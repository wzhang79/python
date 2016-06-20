from abc import ABCMeta,abstractmethod
import numpy as np

class Strategy(object):
	__metaclass__=ABCMeta

	@abstractmethod
	def generate_signals(self):
		raise NotImplementedError("Should implement generate_signals()!")

class Portfolio(object):
	__metaclass__=ABCMeta

	@abstractmethod
	def generate_positions(self):
		raise NotImplementedError("Should implement generate_positions()!")

	@abstractmethod
	def backtest_portfolio(self):
		raise NotImplementedError("Should implement backtest_portfolio()!")

class Performance(object):
	def __init__(self,portfolio):
		self.portfolio=portfolio

	def generate_performance(self,rf=0.0):
		cumret=(1+self.portfolio['returns']).cumprod()
		ret_avg=self.portfolio['returns'].mean()
		std=self.portfolio['returns'].std()
		sharp_ratio=np.sqrt(252)*(ret_avg-rf)/std
		return cumret,sharp_ratio
