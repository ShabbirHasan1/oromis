from alice_blue import AliceBlue, LiveFeedType, TransactionType, ProductType, OrderType
import pandas as pd
import datetime
from time import sleep
import utilities as ut
import os

alice = ut.loginAlice()

# ticker = 'BANKNIFTY'
# fair = 2600
# target = 750
# base = 100
# tradeStr = 34500
# ongoing = False #1 if buy spread, -1 if sell spread
# quantity = 25

ticker = 'NIFTY'
fair = 1516
target = 400
base = 50
tradeStr = 17500
ongoing = False #1 if buy spread, -1 if sell spread
quantity = 50

# month_exp = datetime.datetime(2021,9,30,15,30,0)
month_exp = datetime.datetime(2021,10,28,15,30,0)
week_exp = datetime.datetime(2021,9,16,15,30,0)

strikes = [i for i in range(16500,18500,base)]
# strikes = [i for i in range(33500,35500,base)]


mins = 1

up = fair+target
down = fair-target

symbol = ut.set_symbol(ticker)
indScrip = alice.get_instrument_by_symbol('NSE', symbol)

futScrip = alice.get_instrument_for_fno(symbol = ticker, expiry_date = month_exp.date(), is_fut = True, strike = None, is_CE = False)
lotSize = float(futScrip.lot_size)

callDic = {strike: alice.get_instrument_for_fno(symbol = ticker, expiry_date=week_exp.date(), is_fut=False, strike = strike, is_CE=True) for strike in strikes}
putDic = {strike: alice.get_instrument_for_fno(symbol = ticker, expiry_date=week_exp.date(), is_fut=False, strike = strike, is_CE=False) for strike in strikes}

trackers = ['futAsk','futBid','ind','atmStrike','ongoing']
active = {tracker:None for tracker in trackers}
active['ongoing'] = ongoing
active['tradeStrike'] = tradeStr
socket_opened = False

opts = pd.DataFrame(index=strikes)

def event_handler_quote_update(message):
	messageSymbol = message['instrument'].symbol
	if (messageSymbol == futScrip.symbol):
		bestbid = message['bid_prices'][0]
		bestask = message['ask_prices'][0]
		active['futAsk'] = bestask
		active['futBid'] = bestbid

	elif (messageSymbol == indScrip.symbol):
		lastPrice = message['ltp']
		active['ind'] = lastPrice
		active['atmStrike'] = base * round(active['ind']/base)

	else:
		bestbid = message['bid_prices'][0]
		bestask = message['ask_prices'][0]
		if (messageSymbol.split()[-1]=='CE'):
			opts.loc[int(float(messageSymbol.split()[-2])),'callAsk'] = bestask
			opts.loc[int(float(messageSymbol.split()[-2])),'callBid'] = bestbid
		elif (messageSymbol.split()[-1]=='PE'):
			opts.loc[int(float(messageSymbol.split()[-2])),'putAsk'] = bestask
			opts.loc[int(float(messageSymbol.split()[-2])),'putBid'] = bestbid

def open_callback():
	global socket_opened
	socket_opened = True

def run_strategy():
	#########INITIALIZE SOCKET#####################
	bre = False
	alice.start_websocket(subscribe_callback=event_handler_quote_update,
						socket_open_callback=open_callback,
						run_in_background=True)
	while(socket_opened == False):    # wait till socket open & then subscribe
		pass

	callScrips = list(callDic.values())
	putScrips = list(putDic.values())
	alice.subscribe(indScrip,LiveFeedType.COMPACT)
	alice.subscribe(futScrip, LiveFeedType.SNAPQUOTE)
	alice.subscribe(callScrips, LiveFeedType.SNAPQUOTE)
	alice.subscribe(putScrips, LiveFeedType.SNAPQUOTE)

	print("Script Start Time :: " + str(datetime.datetime.now()))

	sleep(30)
	print(active)
	#########INITIALIZE SOCKET#####################

	while True:

		abhi = datetime.datetime.now()
		stop_script = ut.checkStop()


		if stop_script:
			break

		opts['buySpread'] = (active['futAsk'] + opts.putAsk - opts.callBid - opts.index)*lotSize
		opts['sellSpread'] = (active['futBid'] + opts.putBid - opts.callAsk - opts.index)*lotSize


		if (abhi.time()<datetime.time(9,18)):			
			os.system('clear')
			print(active)
			sleep(1)
			continue

		if not active['ongoing']:
			atm = active['atmStrike']
			if (opts.loc[atm,'buySpread']<=down):
				putScrip = putDic[atm]
				callScrip = callDic[atm]

				ut.buySpread(alice,putScrip,callScrip,futScrip,quantity)

				active['ongoing'] = 1
				active['tradeStrike'] = atm
				print('########################################################')
				print(abhi)
				print(active)
				print(f"Bought: {putScrip.symbol} at {opts.loc[atm,'putAsk']}")
				print(f"Bought: {futScrip.symbol}  at {active['futAsk']}")
				print(f"Sold: {callScrip.symbol}  at {opts.loc[atm,'callBid']}")
				print(f"buySpreadEntry: {opts.loc[atm,'buySpread']}")
				print('########################################################')
				# sleep(2)



			if (opts.loc[atm,'sellSpread']>=up):
				putScrip = putDic[atm]
				callScrip = callDic[atm]

				ut.sellSpread(alice,putScrip,callScrip,futScrip,quantity)
				active['tradeStrike'] = atm

				active['ongoing'] = -1
				print('########################################################')
				print(abhi)
				print(active)
				print(f"Bought: {callScrip.symbol}  at {opts.loc[atm,'callAsk']}")
				print(f"Sold: {futScrip.symbol}  at {active['futBid']}")
				print(f"Sold: {putScrip.symbol} at {opts.loc[atm,'putBid']}")
				print(f"sellSpreadEntry: {opts.loc[atm,'sellSpread']}")
				print('########################################################')
				# sleep(2)

		if active['ongoing']==1:
			atm = active['tradeStrike']
			putScrip = putDic[atm]
			callScrip = callDic[atm]

			if (opts.loc[active['tradeStrike'],'sellSpread']>=fair):

				ut.sellSpread(alice,putScrip,callScrip,futScrip,quantity)
				active['tradeStrike'] = None
				active['ongoing'] = False
				print('*********************************************************')
				print(abhi)
				print(active)
				print(f"Bought: {callScrip.symbol}  at {opts.loc[atm,'callAsk']}")
				print(f"Sold: {putScrip.symbol} at {opts.loc[atm,'putBid']}")
				print(f"Sold: {futScrip.symbol}  at {active['futBid']}")
				print(f"sellSpreadExit: {opts.loc[atm,'sellSpread']}")
				print('*********************************************************')

		elif active['ongoing']==-1:
			atm = active['tradeStrike']
			putScrip = putDic[atm]
			callScrip = callDic[atm]
			if (opts.loc[active['tradeStrike'],'buySpread']<=fair):

				ut.buySpread(alice,putScrip,callScrip,futScrip,quantity)
				active['tradeStrike'] = None
				active['ongoing'] = False
				print('*********************************************************')
				print(abhi)
				print(active)
				print(f"Bought: {putScrip.symbol} at {opts.loc[atm,'putAsk']}")
				print(f"Bought: {futScrip.symbol}  at {active['futAsk']}")
				print(f"Sold: {callScrip.symbol}  at {opts.loc[atm,'callBid']}")
				print(f"buySpreadExit: {opts.loc[atm,'buySpread']}")
				print('*********************************************************')

		# sleep(0.1)
		# if ( (abhi.minute%mins == 0) &  (abhi.second==0)):
		# 	print(abhi)
		# 	print(active)
		# 	print(opts.loc[active['atmStrike']])
		# 	print('')
		# 	sleep(1)




if __name__ == "__main__":
	run_strategy()
