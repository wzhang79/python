import datetime
import numpy as np
import pandas as pd
import sklearn
from pandas.io.data import DataReader
from sklearn.linear_model import LogisticRegression
from sklearn.lda import LDA
from sklearn.qda import QDA

def create_lagged_series(symbol,start_date,end_date,lags=5):
	ts=DataReader(symbol,"yahoo",start_date-datetime.timedelta(days=365),end_date)
	tslag=pd.DataFrame(index=ts.index)
	tslag["Today"]=ts["Adj Close"]
	tslag["Volume"]=ts["Volume"]
	for i in xrange(0,lags):
		tslag["Lag%s" % str(i+1)]=ts["Adj Close"].shift(i+1)
	tsret=pd.DataFrame(index=tslag.index)
	tsret["Volume"]=tslag["Volume"]
	tsret["Today"]=tslag["Today"].pct_change()*100.0
	for i,x in enumerate(tsret["Today"]):
		if(abs(x)<0.0001):
			tsret["Today"][i]=0.0001
	for i in xrange(0,lags):
		tsret["Lag%s" % str(i+1)]=tslag["Lag%s" % str(i+1)].pct_change()*100.0
	tsret["Direction"]=np.sign(tsret["Today"])
	tsret=tsret[tsret.index>=start_date]
	return tsret

def fit_model(name,model,x_train,y_train,x_test,pred):
	model.fit(x_train,y_train)
	pred[name]=model.predict(x_test)
	pred["%s_Correct" % name]=(1.0+pred[name]*pred["Actual"])/2.0
	hit_rate=np.mean(pred["%s_Correct" % name])
	print("%s:%.3f" % (name,hit_rate))

if __name__=="__main__":
	symbol='^GSPC'
	start_date=datetime.datetime(2001,1,10)
	end_date=datetime.datetime(2005,12,31)
	snpret=create_lagged_series(symbol,start_date,end_date)
	X=snpret[['Lag1','Lag2']]
	Y=snpret['Direction']
	start_test=datetime.datetime(2005,1,1)
	x_train=X[X.index<start_test]
	x_test=X[X.index>=start_test]
	y_train=Y[Y.index<start_test]
	y_test=Y[Y.index>=start_test]

	pred=pd.DataFrame(index=y_test.index)
	pred['Actual']=y_test
	print('Hit Rates:')
	models=[('LR',LogisticRegression()),('LDA',LDA()),('QDA',QDA())]
	for m in models:
		fit_model(m[0],m[1],x_train,y_train,x_test,pred)
