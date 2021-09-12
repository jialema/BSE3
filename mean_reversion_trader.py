from trader import Trader
import random
import numpy as np


class MeanReversionTrader(Trader):
	def __init__(self):
		super(MeanReversionTrader, self).__init__()
		self.trader_id = "mean reversion trader"
		self.delta_mr = 0.40
		self.v_mr = 1
		self.alpha = 0.94
		self.ema_t = 0
		# this is an empirical value, given by author
		self.k = 0.01
		self.sigma_t = None
		self.all_ema = []

	def work(self, exchange, cur_time, logger):
		order = None
		best_bid_price = exchange.bids.best_price
		best_ask_price = exchange.asks.best_price
		if len(exchange.prices) == 0:
			return None
		if random.random() < self.delta_mr:
			self.compute_ema(exchange)
			# sell
			if exchange.price - self.ema_t >= self.k * self.sigma_t:
				if best_ask_price is None:
					return None
				ask_price = best_ask_price - exchange.tick_size
				order = self.sell(ask_price, self.v_mr, cur_time)
			elif self.ema_t - exchange.price >= self.k * self.sigma_t:
				# buy
				if best_bid_price is None:
					return None
				bid_price = best_bid_price + exchange.tick_size
				order = self.buy(bid_price, self.v_mr, cur_time)
			logger.debug(order)
		return order

	def compute_ema(self, exchange):
		"""
		compute the exponential moving average of the asset price, ema_t, and
		the standard deviation of all ema.
		@param exchange: exchange
		@return: None
		"""
		# if (len(exchange.prices) - len(self.all_ema)) / len(exchange.prices) < 0.1:
		# 	return
		# length_to_be_processed = len(exchange.all_deal_prices) - len(self.all_ema)
		# for price_t in exchange.all_deal_prices[-length_to_be_processed:]:
		# 	self.ema_t = self.ema_t + self.alpha * (price_t - self.ema_t)
		# 	self.all_ema.append(self.ema_t)
		# self.sigma_t = np.std(self.all_ema, ddof=1)

		price_t = exchange.price
		self.ema_t = self.ema_t + self.alpha * (price_t - self.ema_t)
		self.all_ema.append(self.ema_t)
		if len(self.all_ema) > 1000:
			self.sigma_t = np.std(self.all_ema[-1000:], ddof=1)
		else:
			self.sigma_t = np.std(self.all_ema, ddof=1)
