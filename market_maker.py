from trader import Trader
from order import Order
import random
import pandas as pd
import time


class MarketMaker(Trader):
	"""
	@author Jiale Ma
	"""

	def __init__(self):
		super(MarketMaker, self).__init__()
		self.trader_id = "market maker"
		self.delta_mm = 0.10
		self.quantity_min = 1
		self.quantity_max = 200000
		self.rolling_mean_window_size = 50

	def work(self, exchange, cur_time):
		"""
		prepare orders to be sent to exchange
		"""
		ask_order = None
		bid_order = None

		"""
		If there is no best price, the market maker does not operate, because there is no trading demand.
		The market maker is to provide market liquidity.
		"""
		if exchange.bids.best_price is not None or exchange.asks.best_price is not None:
			if exchange.bids.best_price is None:
				best_bid_price = exchange.price
				best_ask_price = exchange.asks.best_price
			elif exchange.asks.best_price is None:
				best_bid_price = exchange.bids.best_price
				best_ask_price = exchange.price
			else:
				best_bid_price = exchange.bids.best_price
				best_ask_price = exchange.asks.best_price
		else:
			return ask_order, bid_order

		exchange_all_deal_prices = exchange.all_deal_prices[:]
		# if the number of the dealt prices is not enough, the rolling-mean cannot be performed.
		if len(exchange_all_deal_prices) < 2:
			return ask_order, bid_order
		# market maker sent orders to exchange according to probability delta_mm
		if random.random() < self.delta_mm:
			quantity_large = random.randint(self.quantity_min, self.quantity_max)
			quantity_small = 1
			if self.predict_next_order(exchange_all_deal_prices) == "buy":
				ask_order = self.sell(best_ask_price, quantity_large, cur_time)
				bid_order = self.buy(best_bid_price, quantity_small, cur_time)
			else:
				bid_order = self.buy(best_bid_price, quantity_large, cur_time)
				ask_order = self.sell(best_ask_price, quantity_small, cur_time)
		return ask_order, bid_order

	def predict_next_order(self, exchange_all_deal_prices):
		"""
		Predict the type of next order, buy or sell.
		If buy, return true. Otherwise, return false.
		"""
		last_price = self.compute_rolling_mean(exchange_all_deal_prices)
		penultimate_price = self.compute_rolling_mean(exchange_all_deal_prices[:-1])
		# price drop, the type of next order is sell
		if last_price < penultimate_price:
			return "sell"
		else:
			# price rise, the type of next order is buy
			return "buy"

	def compute_rolling_mean(self, exchange_all_deal_prices):
		if len(exchange_all_deal_prices) < self.rolling_mean_window_size:
			rolling_mean_price = sum(exchange_all_deal_prices) / len(exchange_all_deal_prices)
		else:
			rolling_mean_price = sum(exchange_all_deal_prices[-self.rolling_mean_window_size:]) / self.rolling_mean_window_size
		return rolling_mean_price

