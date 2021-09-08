from exchange import Exchange
from market_maker import MarketMaker
from liquidity_consumer import LiquidityConsumer
from momentum_trader import MomentumTrader
from mean_reversion_trader import MeanReversionTrader
from noise_trader import NoiseTrader
import util
from pprint import pprint
import os
import matplotlib.pyplot as plt
import statsmodels.tsa.api as smt
import pandas as pd
import statistics

exchange = Exchange()
print(exchange)
market_maker = MarketMaker()
print(market_maker)
liquidity_consumer = LiquidityConsumer()
print(liquidity_consumer)
momentum_trader = MomentumTrader()
print(momentum_trader)
mean_reversion_trader = MeanReversionTrader()
print(mean_reversion_trader)
noise_trader = NoiseTrader()
print(noise_trader)

traders = dict()
traders[market_maker.trader_id] = market_maker
traders[liquidity_consumer.trader_id] = liquidity_consumer
traders[momentum_trader.trader_id] = momentum_trader
traders[mean_reversion_trader.trader_id] = mean_reversion_trader
traders[noise_trader.trader_id] = noise_trader

data_dir = "data"
if not os.path.exists(data_dir):
	os.mkdir(data_dir)
logs_dir = "logs"
if not os.path.exists(logs_dir):
	os.mkdir(logs_dir)
logger = util.create_log(os.path.join(logs_dir, "bse.log"))


def main():
	"""
	a simulated day is divided into 300,000 periods, 
	# approximately the number of 10ths of a second in an 8.5h trading day
	"""
	mm_order = {"bids": [], "asks": []}

	cur_time = 0
	# total_time = 306000
	total_time = 200000
	while cur_time < total_time:
		if cur_time % 1000 == 0:
			print("\ntime: {}".format(cur_time))

		# market maker
		# print("market maker")
		ask_order, bid_order = market_maker.work(exchange, cur_time)
		if ask_order is not None or bid_order is not None:
			# cancel any existing orders from market maker
			exchange.del_trader_all_orders(market_maker.trader_id, ["Bid", "Ask"], cur_time)
			if ask_order is not None:
				mm_order["asks"].append(ask_order)
				# sent ask order to exchange
				trades = exchange.process_order(cur_time, ask_order, False)
				util.process_trades(trades, traders, ask_order, cur_time)
			if bid_order is not None:
				mm_order["bids"].append(bid_order)
				# sent bid order to exchange
				trades = exchange.process_order(cur_time, bid_order, False)
				util.process_trades(trades, traders, bid_order, cur_time)

		# liquidity consumer
		if cur_time == 0:
			# initialize internal parameters at start of day
			liquidity_consumer.make_decision()
		order = liquidity_consumer.work(exchange, cur_time)
		if order is not None:
			trades = exchange.process_order(cur_time, order, False)
			util.process_trades(trades, traders, order, cur_time)

		# momentum trader
		order = momentum_trader.work(exchange, cur_time)
		if order is not None:
			trades = exchange.process_order(cur_time, order, False)
			util.process_trades(trades, traders, order, cur_time)

		# mean reversion trader
		order = mean_reversion_trader.work(exchange, cur_time)
		if order is not None:
			trades = exchange.process_order(cur_time, order, False)
			util.process_trades(trades, traders, order, cur_time)

		# noise trader
		order = noise_trader.work(exchange, cur_time)
		if order is not None:
			trades = exchange.process_order(cur_time, order, False)
			util.process_trades(trades, traders, order, cur_time)
		exchange.prices.append(exchange.price)
		logger.debug(exchange.price)
		cur_time += 1

	exchange.tape_dump(os.path.join(data_dir, "transaction_records.csv"), "w", "keep")
	exchange.exception_transaction_dump(os.path.join(data_dir, "exception_records.csv"), "w")
	exchange.orders_dump(os.path.join(data_dir, "orders.csv"), "w")

	# print(statistics.auto_correlation(exchange.orders_signs, 1)[0])
	# print(statistics.hurst(exchange.orders_signs))
	# print(statistics.find_price_spike(exchange.all_deal_prices))
	util.plot_price_trend(exchange)
	util.plot_order_scatter(mm_order)
	# print(statistics.find_price_spike(exchange.trade_price_rolling_mean))

	# statistics.concave_price_impact(exchange)
	# statistics.volatility_clustering(exchange)
	# statistics.fat_tailed_distribution(exchange)
	statistics.return_auto_correlation(exchange)


if __name__ == "__main__":
	main()
