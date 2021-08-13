from trader import Trader
import random


class MomentumTrader(Trader):
	def __init__(self):
		super(MomentumTrader, self).__init__()
		self.trader_id = "momentum trader"
		self.delta_mt = 0.40
		self.n_r = 6
		self.k = 0.001
		self.wealth = 1000000

	def work(self, exchange, cur_time):
		order = None
		if random.random() < self.delta_mt:
			roc_t = (exchange.all_deal_prices[-1] - exchange.all_deal_prices[-self.n_r]) \
					/ exchange.all_deal_prices[-self.n_r]
			v_t = abs(roc_t) * self.wealth
			if roc_t >= self.k:
				best_price = exchange.asks.lob_anon[0][0]
				order = self.buy(best_price, v_t, cur_time)
			elif roc_t <= -self.k:
				best_price = exchange.bids.lob_anon[-1][0]
				order = self.sell(best_price, v_t, cur_time)

			if self.buy_or_sell == "buy":
				best_price = exchange.asks.lob_anon[0][0]
				order = self.buy(best_price, v_t, cur_time)
			elif self.buy_or_sell == "sell":
				best_price = exchange.bids.lob_anon[-1][0]
				order = self.sell(best_price, v_t, cur_time)
		return order
