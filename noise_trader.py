import sys
from trader import Trader
import random
import math


class NoiseTrader(Trader):
	"""
	The implementation of noise trader.
	@author Jiale Ma
	"""
	def __init__(self):
		super(NoiseTrader, self).__init__()
		self.trader_id = "noise trader"
		self.delta_nt = 0.75
		self.buy_or_sell_prob = 0.50
		# market order probability
		self.alpha_m = 0.03
		# limit order probability
		self.alpha_l = 0.54
		# cancel order probability
		self.alpha_c = 0.43
		# market order size
		self.mu_mo = 7
		self.sigma_mo = 0.1
		# limit order size
		self.mu_lo = 8
		self.sigma_lo = 0.7
		# off-spread relative price, 0.05, 0.03 with min(..., 0.2)
		self.x_min_off_spr = 0.03
		self.beta_off_spr = 2.72
		# crossing limit order
		self.alpha_crs = 0.003
		# inside-spread limit order
		self.alpha_in_spr = 0.098
		# spread limit order
		self.alpha_spr = 0.173
		# off-spread limit order
		self.alpha_off_spr = 0.426

	def work(self, exchange, cur_time):
		"""
		The main logic of noise traders
		:param exchange: the instance of Exchange Class
		:param cur_time: current time
		:return: the order to be submitted
		"""
		order = None
		if random.random() < self.delta_nt:
			if random.random() <= self.buy_or_sell_prob:
				buy_or_sell = "buy"
			else:
				buy_or_sell = "sell"

			best_bid_price = exchange.bids.best_price
			best_ask_price = exchange.asks.best_price
			if best_bid_price is None:
				best_bid_price = exchange.price
			if best_ask_price is None:
				best_ask_price = exchange.price

			random_action_prob = random.random()
			# submit market order
			if random_action_prob < self.alpha_m:
				q_t = int(math.exp(self.mu_mo + self.sigma_mo * random.random()) + 0.5)
				order = self.submit_order(buy_or_sell, q_t, None, "submit market order", exchange, cur_time)
			elif random_action_prob < self.alpha_m + self.alpha_l:
				# submit limit order
				random_limit_order_prob = random.random()
				q_t = int(math.exp(self.mu_lo + self.sigma_lo * random.random()) + 0.5)
				# cross limit order
				if random_limit_order_prob < self.alpha_crs:
					order = self.submit_order(buy_or_sell, q_t, None, "cross limit order", exchange, cur_time)
				elif random_limit_order_prob < self.alpha_crs + self.alpha_in_spr:
					# inside spread limit order
					price_in_spr = random.uniform(best_bid_price, best_ask_price)
					order = self.submit_order(buy_or_sell, q_t, price_in_spr, "", exchange, cur_time)
				elif random_limit_order_prob < self.alpha_crs + self.alpha_in_spr + self.alpha_spr:
					# spread limit order
					order = self.submit_order(buy_or_sell, q_t, None, "spread limit order", exchange, cur_time)
				else:
					# off-spread limit order
					price_off_spr = self.x_min_off_spr * (1 - random.uniform(0, 1)) ** (-1 / (self.beta_off_spr - 1))
					price_off_spr = min(price_off_spr, 0.2)
					order = self.submit_order(buy_or_sell, q_t, price_off_spr, "off-spread limit order", exchange, cur_time)
			else:
				# cancel limit order
				if buy_or_sell == "buy":
					order_type = "Bid"
				else:
					order_type = "Ask"
				# exchange.del_oldest_order(self.trader_id, order_type, cur_time)
				exchange.del_trader_all_orders(self.trader_id, [order_type], cur_time)
		return order

	def submit_order(self, buy_or_sell=None, q_t=None, price=None, action_type="", exchange=None, cur_time=None):
		if q_t == 0:
			sys.exit("[Error] bad q_t value")
		best_bid_price = exchange.bids.best_price
		best_ask_price = exchange.asks.best_price
		if best_bid_price is None:
			best_bid_price = exchange.price
		if best_ask_price is None:
			best_ask_price = exchange.price
		if buy_or_sell == "buy":
			if action_type == "off-spread limit order":
				"""
				If there is no valid counterparty in the counterparty queue in the limit order book, 
				the order will be cancelled directly.
				"""
				price = best_bid_price - price
				order = self.buy(price, q_t, cur_time)
			elif price is not None:
				order = self.buy(price, q_t, cur_time)
			elif action_type in ["submit market order", "cross limit order"]:
				order = self.buy(best_ask_price, q_t, cur_time)
			elif action_type == "spread limit order":
				order = self.buy(best_bid_price, q_t, cur_time)
			else:
				sys.exit("[Error] bad action_type value")
		elif buy_or_sell == "sell":
			if action_type == "off-spread limit order":
				price = best_ask_price + price
				order = self.sell(price, q_t, cur_time)
			elif price is not None:
				order = self.sell(price, q_t, cur_time)
			elif action_type in ["submit market order", "cross limit order"]:
				order = self.sell(best_bid_price, q_t, cur_time)
			elif action_type == "spread limit order":
				order = self.sell(best_ask_price, q_t, cur_time)
			else:
				sys.exit("[Error] bad action_type value")
		else:
			sys.exit("[Error] bad buy_or_sell value")
		return order
