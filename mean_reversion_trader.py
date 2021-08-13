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
		# this is an empirical value
		self.k = 1
		self.sigma_t = None
		self.all_ema = []

	def work(self, exchange, cur_time):
		order = None
		if random.random() < self.delta_mr:
			self.compute_ema(exchange)
			# sell high
			if exchange.price - self.ema_t >= self.k * self.sigma_t:
				ask_price = exchange.asks.best_price + exchange.tick_size
				order = self.sell(ask_price, self.v_mr, cur_time)
			elif self.ema_t - exchange.price >= self.k * self.sigma_t:
				# buy low
				bid_price = exchange.bids.best_price - exchange.tick_size
				order = self.buy(bid_price, self.v_mr, cur_time)
		return order

	def compute_ema(self, exchange):
		"""
		compute the exponential moving average of the asset price, ema_t, and
		the standard deviation of all ema.
		@param exchange: exchange
		@return: None
		"""
		length_to_be_processed = len(exchange.all_deal_prices) - len(self.all_ema)
		for price_t in range(exchange.all_deal_prices[-length_to_be_processed:]):
			self.ema_t = self.ema_t + self.alpha * (price_t - self.ema_t)
			self.all_ema.append(self.ema_t)
		self.sigma_t = np.std(self.ema_t, ddof=1)
