from trader import Trader
import random
import sys


class LiquidityConsumer(Trader):
	def __init__(self):
		super(LiquidityConsumer, self).__init__()
		self.trader_id = "liquidity consumer"
		# buy or sell
		self.buy_or_sell = None
		self.h_min = 1
		self.h_max = 100000
		self.h_t = None
		self.delta_lc = 0.10

	def make_decision(self):
		if random.random() < 0.5:
			self.buy_or_sell = "buy"
		else:
			self.buy_or_sell = "sell"
		self.h_t = random.randint(self.h_min, self.h_max)

	def work(self, exchange, cur_time):
		order = None
		# look at the current volume available at the opposite best price, phi_t
		if self.buy_or_sell == "buy":
			if len(exchange.asks.lob_anon) == 0:
				return None
			phi_t = exchange.asks.lob_anon[0][1]
			best_price = exchange.asks.lob_anon[0][0]
		elif self.buy_or_sell == "sell":
			if len(exchange.bids.lob_anon) == 0:
				return None
			phi_t = exchange.bids.lob_anon[-1][1]
			best_price = exchange.bids.lob_anon[-1][0]
		else:
			sys.exit("[Error] bad self.buy_or_sell value.")
		if random.random() < self.delta_lc and self.h_t > 0:
			"""
			If the remaining volume of trader's large order, self.h_t, is less than phi_t, the agent 
			sets this periods volume to v_t = self.h_t, otherwise he takes all available volume at 
			the best price, v_t = phi_t.
			"""
			if self.h_t < phi_t:
				v_t = self.h_t
			else:
				v_t = phi_t
			if self.buy_or_sell == "buy":
				order = self.buy(best_price, v_t, cur_time)
			elif self.buy_or_sell == "sell":
				order = self.sell(best_price, v_t, cur_time)
			else:
				sys.exit("[Error] bad self.buy_or_sell value.")
			self.h_t -= v_t
		return order

