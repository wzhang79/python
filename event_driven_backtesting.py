import time
import datetime
from Queue import Queue
from data import HistoricCSVDataHandler
from data import DataBaseDataHandler
from strategy import BuyAndHoldStrategy, MovingAverageCrossStrategy
from portfolio import NaivePortfolio
from execution import SimulatedExecutionHandler

def test():
	events=Queue()
	csv_dir='/Users/weileizhang/Downloads/'
	symbol_list=['XOM']
	#start_date=datetime.datetime(2013,1,1)
        #end_date=datetime.datetime(2015,1,5)
	#bars=HistoricCSVDataHandler(events,csv_dir,symbol_list,start_date,end_date)
	start_date='2010-1-1'
	end_date='2015-1-1'
	bars=DataBaseDataHandler(events,symbol_list,start_date,end_date)
#	strategy=BuyAndHoldStrategy(bars,events)
	strategy=MovingAverageCrossStrategy(bars,events,short_window=100,long_window=400)
	port=NaivePortfolio(bars,events,start_date,initial_capital=100000.0)
	broker=SimulatedExecutionHandler(events)

	while True:
		if bars.continue_backtest==True:
			bars.update_bars()
		else:
			break

		while True:
			try:
				event=events.get(False)
			except:
				break
			else:
				if event is not None:
					if event.type=='MARKET':
						strategy.calculate_signals(event)
						port.update_timeindex(event)

					elif event.type=='SIGNAL':
						port.update_signal(event)

					elif event.type=='ORDER':
						broker.execute_order(event)

					elif event.type=='FILL':
						port.update_fill(event)
		
	port.create_equity_curve_dataframe()
	stats=port.output_summary_stats()	
	print(stats)

if __name__=='__main__':
	test()
