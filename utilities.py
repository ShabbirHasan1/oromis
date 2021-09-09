import datetime
import aliceConfig
from alice_blue import AliceBlue, TransactionType, ProductType, OrderType
import os
from time import sleep
# import logging
# logging.basicConfig(level=logging.DEBUG)


def checkStop():
	if(datetime.datetime.now().second == 0 or datetime.datetime.now().second == 30):
		# NOTE This is just an example to stop script without using `control + c` Keyboard Interrupt
		# It checks whether the stop.txt has word stop
		# This check is done every 30 seconds
		stop_script = open('stop.txt', 'r').read().strip()
		checkFlag = (stop_script == 'stop')
		if(checkFlag):
			print(stop_script + " time :: " + str(datetime.datetime.now()))
			print('exiting script')
		return checkFlag


def loginAlice():
	access_token = AliceBlue.login_and_get_access_token(username=aliceConfig.login_id, password=aliceConfig.password, twoFA=aliceConfig.twofa,  api_secret=aliceConfig.secret, app_id=aliceConfig.app_id)
	while True:
		try:
			alice = AliceBlue(username=aliceConfig.login_id, password=aliceConfig.password, access_token=access_token, master_contracts_to_download=['NSE','NFO'])
			break
		except:
			print('logging alice in...')
			os.system('clear')
			sleep(1)	
	return alice

def buySpread(alice,putScrip,callScrip,futScrip,quantity):
	order1 = alice.place_order(transaction_type = TransactionType.Buy,
					 instrument = putScrip,
					 quantity = quantity,
					 order_type = OrderType.Market,
					 product_type = ProductType.Delivery,
					 price = 0.0,
					 trigger_price = None,
					 stop_loss = None,
					 square_off = None,
					 trailing_sl = None,
					 is_amo = False)
	order2 = alice.place_order(transaction_type = TransactionType.Buy,
					 instrument = futScrip,
					 quantity = quantity,
					 order_type = OrderType.Market,
					 product_type = ProductType.Delivery,
					 price = 0.0,
					 trigger_price = None,
					 stop_loss = None,
					 square_off = None,
					 trailing_sl = None,
					 is_amo = False)
	order3 = alice.place_order(transaction_type = TransactionType.Sell,
					 instrument = callScrip,
					 quantity = quantity,
					 order_type = OrderType.Market,
					 product_type = ProductType.Delivery,
					 price = 0.0,
					 trigger_price = None,
					 stop_loss = None,
					 square_off = None,
					 trailing_sl = None,
					 is_amo = False)
	return order1,order2,order3


def sellSpread(alice,putScrip,callScrip,futScrip,quantity):
	order1 = alice.place_order(transaction_type = TransactionType.Buy,
					 instrument = callScrip,
					 quantity = quantity,
					 order_type = OrderType.Market,
					 product_type = ProductType.Delivery,
					 price = 0.0,
					 trigger_price = None,
					 stop_loss = None,
					 square_off = None,
					 trailing_sl = None,
					 is_amo = False)
	order2 = alice.place_order(transaction_type = TransactionType.Sell,
					 instrument = futScrip,
					 quantity = quantity,
					 order_type = OrderType.Market,
					 product_type = ProductType.Delivery,
					 price = 0.0,
					 trigger_price = None,
					 stop_loss = None,
					 square_off = None,
					 trailing_sl = None,
					 is_amo = False)
	order3 = alice.place_order(transaction_type = TransactionType.Sell,
					 instrument = putScrip,
					 quantity = quantity,
					 order_type = OrderType.Market,
					 product_type = ProductType.Delivery,
					 price = 0.0,
					 trigger_price = None,
					 stop_loss = None,
					 square_off = None,
					 trailing_sl = None,
					 is_amo = False)
	return order1,order2,order3

def set_symbol(ticker):
	if ticker == 'NIFTY':
		symbol = 'Nifty 50'
	elif ticker == 'BANKNIFTY':
		symbol = 'Nifty Bank'
	else:
		symbol = ticker
	return symbol


