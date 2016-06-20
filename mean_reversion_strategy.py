import matplotlib.pyplot as plt
import numpy as np
import os, os.path
import pandas as pd

def create_pairs_dataframe(datadir,symbols):
	print('Importing CSV data...')
	sym1=pd.io.parsers.read_csv(os.path.join(datadir,'%s.csv' % symbols[0]),header=0,index_col=0,names=['datetime','open','high','low','close','volume','adj_close'])
	sym2=pd.io.parsers.read_csv(os.path.join(datadir,'%s.csv' % symbols[1]),header=0,index_col=0,names=['datetime','open','high','low','close','volume','adj_close'])
	print('Constructing dual matrix for %s and %s...' % symbols)
	pairs=pd.DataFrame(index=sym1.index)
	pairs['%s_close' % symbols[0].lower()]=sym1['close']
	pairs['%s_close' % symbols[1].lower()]=sym2['close']
	pairs=pairs.dropna()
	return pairs

def calculate_spread_zscore(pairs,symbols,lookback=100):
	print('Fitting the rolling Linear Regression...')
	model=pd.ols(y=pairs['%s_close' % symbols[0].lower()],
			x=pairs['%s_close' % symbols[1].lower()],
			window=lookback)
	pairs['hedge_ratio']=model.beta['x']
	pairs=pairs.dropna()
	print('Creating the spread/zscore columns...')
	pairs['spread']=pairs['spy_close']-pairs['hedge_ratio']*pairs['iwm_close']
	pairs['zscore']=(pairs['spread']-np.mean(pairs['spread']))/np.std(pairs['spread'])
	return pairs

def create_long_short_market_signals(pairs,symbols,z_entry_threshold=2.0,z_exit_threshold=1.0):
	pairs['longs']=(pairs['zscore']<=-z_entry_threshold)*1.0
	pairs['shorts']=(pairs['zscore']>=z_entry_threshold)*1.0
	pairs['exits']=(np.abs(pairs['zscore'])<=z_exit_threshold)*1.0
	pairs['long_market']=0.0
	pairs['short_market']=0.0
	long_market=0
	short_market=0
	print('Calculating when to be in the market (long and short)...')
	for i,b in enumerate(pairs.iterrows()):
		if b[1]['longs']==1.0:
			long_market=1
		if b[1]['shorts']==1.0:
			short_market=1
		if b[1]['exits']==1.0:
			long_market=0
			short_market=0
		pairs.ix[i]['long_market']=long_market
		pairs.ix[i]['short_market']=short_market
	return pairs

def create_portfolio_returns(pairs,symbols):
	sym1=symbols[0].lower()
	sym2=symbols[1].lower()
	print('Constructing a portfolio...')
	portfolio=pd.DataFrame(index=pairs.index)
	portfolio['positions']=pairs['long_market']-pairs['short_market']
	portfolio[sym1]=-1.0*pairs['%s_close' % sym1]*portfolio['positions']
	portfolio[sym2]=pairs['%s_close' % sym2]*portfolio['positions']
	portfolio['total']=portfolio[sym1]+portfolio[sym2]
	print('Constructing the equity curve...')
	portfolio['returns']=portfolio['total'].pct_change()
	portfolio['returns'].fillna(0.0,inplace=True)
	portfolio['returns'].replace([np.inf,-np.inf],0.0,inplace=True)
	portfolio['returns'].replace(-1.0,0.0,inplace=True)
	portfolio['returns']=(portfolio['returns']+1.0).cumprod()
	return portfolio

if __name__=='__main__':
	datadir='/Users/weileizhang/Downloads/'
	symbols=('SPY','IWM')
	lookbacks=range(50,210,10)
	returns=[]
	for lb in lookbacks:
		print('Calculating lookback=%s...' % lb)
		pairs=create_pairs_dataframe(datadir,symbols)
		pairs=calculate_spread_zscore(pairs,symbols,lookback=lb)
		pairs=create_long_short_market_signals(pairs,symbols,2.0,1.0)
		portfolio=create_portfolio_returns(pairs,symbols)
		returns.append(portfolio.ix[-1]['returns'])
	plt.plot(lookbacks,returns,'-o')
	plt.show()
