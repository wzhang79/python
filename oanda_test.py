import httplib
import urllib
import json
import datetime

conn=httplib.HTTPSConnection('api-fxpractice.oanda.com')
headers={'Authorization':'Bearer d68a69e1b415c5df9e784165cc738076-44df76ae79c42ed7a66e1ec1510fb604'}
conn.request('GET','/v1/prices?instruments=USD_CAD',headers=headers)
response=conn.getresponse()
resptext=response.read()
if response.status==200:
	data=json.loads(resptext)
	print(data)
#headers={'Content-Type':'application/x-www-form-urlencoded',
#		'Authorization': 'Bearer d68a69e1b415c5df9e784165cc738076-44df76ae79c42ed7a66e1ec1510fb604'}
#now=datetime.datetime.now()
#expire=now+datetime.timedelta(days=1)
#expire=expire.isoformat('T')+'Z'
#params=urllib.urlencode({'instrument':'USD_CAD',
#			'expiry':expire,
#			'units':50,
#			'type':'limit',
#			'price':1.0,
#			'side':'buy'})
#conn.request('POST','/v1/accounts/7242741/orders',params,headers)
#print(conn.getresponse().read())
