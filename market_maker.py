from trader import Trader
import random


class MarketMaker(Trader):
	"""
	The implementation of market makers in agent-based model
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
		The main logic of market maker agent
		Prepare orders to be sent to exchange
		"""
		ask_order = None
		bid_order = None

		"""
		If there is no best price, the market maker does not operate, because there is no trading demand.
		The market maker is to provide market liquidity.
		"""

		best_bid_price = exchange.bids.best_price
		best_ask_price = exchange.asks.best_price
		# if best_bid_price is None:
		# 	best_bid_price = exchange.price
		# if best_ask_price is None:
		# 	best_ask_price = exchange.price

		if best_bid_price is None or best_ask_price is None:
			return None, None

		# exchange_prices = exchange.all_deal_prices
		exchange_prices = exchange.prices
		# if the number of the dealt prices is not enough, the rolling-mean cannot be performed.
		if len(exchange_prices) < 2:
			return None, None
		# market maker sent orders to exchange according to probability delta_mm
		if random.random() < self.delta_mm:
			quantity_large = random.randint(self.quantity_min, self.quantity_max)
			quantity_small = 1
			next_order_type = self.predict_next_order(exchange_prices)
			if next_order_type == "buy":
				ask_order = self.sell(best_ask_price, quantity_large, cur_time)
				bid_order = self.buy(best_bid_price, quantity_small, cur_time)
			elif next_order_type == "sell":
				bid_order = self.buy(best_bid_price, quantity_large, cur_time)
				ask_order = self.sell(best_ask_price, quantity_small, cur_time)
			else:
				return None, None
		return ask_order, bid_order

	def predict_next_order(self, exchange_prices):
		"""
		Predict the type of next order, buy or sell.
		If buy, return true. Otherwise, return false.
		"""
		last_price = self.compute_rolling_mean(exchange_prices)
		penultimate_price = self.compute_rolling_mean(exchange_prices[:-1])
		# price drop, the type of next order is sell
		if last_price < penultimate_price:
			return "sell"
		elif last_price > penultimate_price:
			# price rise, the type of next order is buy
			return "buy"
		else:
			return None

	def compute_rolling_mean(self, exchange_prices):
		"""
		Compute w-period rolling mean of price
		:param exchange_prices: prices
		:return: the price after rolling mean
		"""
		if len(exchange_prices) < self.rolling_mean_window_size:
			rolling_mean_price = sum(exchange_prices) / len(exchange_prices)
		else:
			rolling_mean_price = sum(exchange_prices[-self.rolling_mean_window_size:]) / self.rolling_mean_window_size
		return rolling_mean_price

