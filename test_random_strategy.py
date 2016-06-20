import random
import httplib
import urllib
import requests
import json
import Queue
import threading
import time
from event import OrderEvent,TickEvent
from setting import STREAM_DOMAIN,API_DOMAIN,ACCESS_TOKEN,ACCOUNT_ID
requests.packages.urllib3.disable_warnings()

class TestRandomStrategy(object):
	def __init__(self,instrument,units,events):
		self.instument=instrument
		self.units=units
		self.events=events
		self.ticks=0

	def calculate_signals(self,event):
		if event.type=='TICK':
			self.ticks+=1
			if self.ticks % 5==0:
				side=random.choice(['BUY','SELL'])
				order=OrderEvent(self.instrument,'market',self.units,side)
				self.events.put(order)

class Execution(object):
	def __init__(self,domain,access_token,account_id):
		self.domain=domain
		self.access_token=access_token
		self.account_id=account_id
		self.conn=self.obtain_connection()

	def obtain_connection(self):
		return httplib.HTTPSConnection(self.domain)

	def execute_order(self,event):
		headers={
			'Content-Type':'application/x-www-form-urlencoded',
			'Authorization':'Bearer'+self.access_token
			}
		params=urllib.urlencode({
			'instrument':event.instrument,
			'units':event.units,
			'type':event.order_type,
			'side':event.side
			})
		self.conn.request(
			'POST',
			'/v1/accounts/%s/orders' % str(self.account_id),
			params,headers
			)
		response=self.conn.getresponse().read()
		print response

class StreamingForexPrices(object):
	def __init__(self,domain,access_token,account_id,instruments,events_queue):
		self.domain=domain
		self.access_token=access_token
		self.account_id=account_id
		self.instruments=instruments
		self.events_queue=events_queue

	def connect_to_stream(self):
		try:
			url='/v1/prices?instruments='+self.instruments
			conn=httplib.HTTPSConnection(self.domain)
			headers={'Authorization':'Bearer '+self.access_token}
			conn.request('GET',url,headers=headers)
			response=conn.getresponse()
			return response
		except Exception as e:
			s.close()
			print('Caught exception when connecting to stream\n'+str(e))

	def stream_to_queue(self):
		response=self.connect_to_stream()
		print(response.status)
		if response.status==200:
			resptext=response.read()
			try:
				data=json.loads(resptext)
			except Exception as e:
				print('Caught exception  when converting message into json'+str(e))
				return
			else:
				print(data)
				instrument=data['prices'][0]['instrument']
				time=data['prices'][0]['time']
				bid=data['prices'][0]['bid']
				ask=data['prices'][0]['ask']
				tev=TickEvent(instrument,time,bid,ask)
				self.events_queue.put(tev)


def trade(events,strategy,execution):
	while True:
		try:
			event=events.get(False)
		except Queue.Empty:
			return
		else:
			if event is not None:
				print(event.type)
				if event.type=='TICK':
					strategy.calculate_signals(event)
				elif event.type=='ORDER':
					print('Executing order!')
					execution.execute_order(event)
		#time.sleep(heartbeat)

if __name__=='__main__':
	heartbeat=0.5
	events=Queue.Queue()
	instrument='USD_CAD'
	units=100
	prices=StreamingForexPrices(API_DOMAIN,ACCESS_TOKEN,ACCOUNT_ID,instrument,events)
	execution=Execution(API_DOMAIN,ACCESS_TOKEN,ACCOUNT_ID)
	strategy=TestRandomStrategy(instrument,units,events)
	trade_thread=threading.Thread(target=trade,args=(events,strategy,execution))
	price_thread=threading.Thread(target=prices.stream_to_queue,args=[])
	trade_thread.start()
	price_thread.start()
