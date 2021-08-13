import sys
from trader import Trader
import random
import math


class NoiseTrader(Trader):
	def __init__(self):
		super(NoiseTrader, self).__init__()
		self.trader_id = "noise trader"
		self.delta_nt = 0.75
		self.buy_or_sell_prob = 0.5
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
		# off-spread relative price
		self.x_min_off_spr = 0.005
		self.beta_off_spr = 2.72
		# crossing limit order
		self.alpha_crs = 0.003
		# inside-spread limit order
		self.alpha_in_spr = 0.098
		# spread limit order
		self.alpha_spr = 0.173
		# off-spread limit order
		self.alpha_off_spr = 0.726

	def work(self, exchange, cur_time):
		order = None
		if random.random() < self.delta_nt:
			if random.random() < self.buy_or_sell_prob:
				buy_or_sell = "buy"
			else:
				buy_or_sell = "sell"
			random_action_prob = random.random()
			# submit market order
			if random_action_prob < self.alpha_m:
				v_t = math.exp(self.mu_mo + self.sigma_mo * random.random())
				order = self.submit_order(buy_or_sell, v_t, None, "submit market order", exchange, cur_time)
			elif random_action_prob < self.alpha_m + self.alpha_l:
				# submit limit order
				random_limit_order_prob = random.random()
				v_t = math.exp(self.mu_lo + self.sigma_lo * random.random())
				# cross limit order
				if random_limit_order_prob < self.alpha_crs:
					order = self.submit_order(buy_or_sell, v_t, None, "cross limit order", exchange, cur_time)
				elif random_limit_order_prob < self.alpha_crs + self.alpha_in_spr:
					# inside spread limit order
					price_in_spr = random.randint(exchange.bids.best_price, exchange.asks.best_price)
					order = self.submit_order(buy_or_sell, v_t, price_in_spr, "", exchange, cur_time)
				elif random_limit_order_prob < self.alpha_crs + self.alpha_in_spr + self.alpha_spr:
					# spread limit order
					order = self.submit_order(buy_or_sell, v_t, None, "spread limit order", exchange, cur_time)
				else:
					# off-spread limit order
					price_off_spr = self.x_min_off_spr * (1 - random.random()) ** (-1 / (self.beta_off_spr - 1))
					order = self.submit_order(buy_or_sell, v_t, price_off_spr, "", exchange, cur_time)
			else:
				# cancel limit order
				self.del_any_existing_orders_by_trader(self.trader_id, cur_time)
		return order

	def submit_order(self, buy_or_sell=None, v_t=None, price=None, action_type="", exchange=None, cur_time=None):
		if buy_or_sell == "buy":
			if price is not None:
				order = self.buy(price, v_t, cur_time)
			elif action_type in ["submit market order", "cross limit order"]:
				best_price = exchange.asks.best_price
				order = self.buy(best_price, v_t, cur_time)
			elif action_type == "spread limit order":
				price = exchange.bids.best_price
				order = self.buy(price, v_t, cur_time)
			else:
				sys.exit("[Error] bad action_type value")
		elif buy_or_sell == "sell":
			if price is not None:
				order = self.sell(price, v_t, cur_time)
			elif action_type in ["submit market order", "cross limit order"]:
				best_price = exchange.bids.best_price
				order = self.sell(best_price, v_t, cur_time)
			elif action_type == "spread limit order":
				price = exchange.asks.best_price
				order = self.sell(price, v_t, cur_time)
			else:
				sys.exit("[Error] bad action_type value")
		else:
			sys.exit("[Error] bad buy_or_sell value")
		return order

	def del_any_existing_orders_by_trader(self, trader_id, cur_time):
		"""
		delete any existing orders from a certain trader
		@param trader_id: ID of a certain trader
		@param cur_time: current time
		"""
		if self.bids.orders.contain(trader_id):
			self.bids.book_del(trader_id)
			cancel_record = {'type': 'Cancel', 'time': cur_time, 'trader_id': trader_id}
			self.tape.append(cancel_record)
		if self.asks.orders.contains(trader_id):
			self.asks.book_del(trader_id)
			cancel_record = {'type': 'Cancel', 'time': cur_time, 'trader_id': trader_id}
			self.tape.append(cancel_record)
