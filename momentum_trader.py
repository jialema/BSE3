from trader import Trader
import random


class MomentumTrader(Trader):
	def __init__(self):
		super(MomentumTrader, self).__init__()
		self.trader_id = "momentum trader"
		self.delta_mt = 0.40
		self.n_r = 6
		self.k = 0.001
		self.wealth = 100000

	def work(self, exchange, cur_time):
		order = None
		if len(exchange.prices) < self.n_r:
			return None
		if random.random() < self.delta_mt:
			roc_t = (exchange.prices[-1] - exchange.prices[-self.n_r]) \
					/ exchange.prices[-self.n_r]
			v_t = int(abs(roc_t) * self.wealth + 0.5)
			if roc_t >= self.k:
				order = self.buy(exchange.asks.best_price, v_t, cur_time)
			elif roc_t <= -self.k:
				order = self.sell(exchange.bids.best_price, v_t, cur_time)
		return order
