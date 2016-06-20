import datetime
import time
from ib.ext.Contract import Contract
from ib.ext.Order import Order
from ib.opt import ibConnection,message
from event import FillEvent,OrderEvent
from execution import ExecutionHandler

class IBExecutionHandler(ExecutionHandler):
	def __init__(self,events,order_routing="SMART",currency="USD"):
		self.events=events
		self.order_routing=order_routing
		sefl.currency=currency
		self.fill_dict={}

		self.tws_conn=self.create_tws_connection()
		self.order_id=self.create_initial_order_id()
		self.register_handlers()

	def _error_handler(self,msg):
		print("Server Error: %s" % msg)
	
	def _reply_handler(self,msg):
		if msg.typeName=="openOrder" and msg.orderId==self.order_id and not self.fill_dict.has_key(msg.orderId):
			self.create_fill_dict_entry(msg)
		if msg.typeName=="orderStatus" and msg.status=="Filled" and self.fill_dict[msg.orderId]["filled"]==False:
			self.create_fill(msg)
		print("Server Response: %s, %s\n" % (msg.typeName,msg))

	def create_tws_connection(self):
		tws_conn=ibConnection()
		tws_conn.connect()
		return tws_conn

	def create_initial_order_id(self):
		return 1

	def register_handlers(self):
		self.tws_conn.register(self._error_handler,'Error')
		self.tws_conn.register(self._reply_handler)

	def create_contract(self,symbol,sec_type,exch,prim_exch,curr):
		contract=Contract()
		contract.m_symbol=symbol
		contract.m_secType=sec_type
		contract.m_exchange=exch
		contract.m_primaryExch=prim_exch
		contract.m_currency=curr
		return contract

	def create_order(self,order_type,quantity,action):
		order=Order()
		order.m_orderType=order_type
		order.m_totalQuantity=quantity
		order.m_action=action
		return order

	def create_fill_dict_entry(self,msg):
		self.fill_dict[msg.orderId]={
			"symbol":msg.contract.m_symbol,
			"exchange":msg.contract.m_exchange,
			"direction":msg.order.m_action,
			"filled":False
		}

	def create_fill(self,msg):
		fd=self.fill_dict[msg.orderId]
		symbol=fd["symbol"]
		exchange=fd["exchange"]
		filled=msg.filled
		direction=fd["direction"]
		fill_cost=msg.avgFillPrice
		fill=FillEvent(datetime.datetime.utcnow(),symbol,exchange,filled,direction,fill_cost)
		self.fill_dict[msg.orderId]["filled"]=True
		self.events.put(fill_event)

	def execute_order(self,event):
		if event.type=='ORDER':
			asset=event.symbol
			asset_type="STK"
			order_type=event.order_type
			quantity=event.quantity
			direction=event.direction
			
			ib_contract=self.create_contract(asset,assect_type,self.order_routing,self.order_routing,self.currency)
			ib_order=self.create_order(order_type,quantity,direction)
			self.tws_conn.placeOrder(self.order_id,ib_contract,ib_order)
			time.sleep(1)
			self.order_id+=1

