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
	cur_time = 0
	# total_time = 300000
	total_time = 200000
	while cur_time < total_time:
		if cur_time % 10000 == 0:
			print("\ntime: {}".format(cur_time))

		# market maker
		# print("market maker")
		ask_order, bid_order = market_maker.work(exchange, cur_time)
		# print(ask_order)
		# print(bid_order)
		if ask_order is not None:
			# cancel any existing orders from market maker
			exchange.del_trader_all_orders(market_maker.trader_id, cur_time)
			# sent ask order to exchange
			trades = exchange.process_order(cur_time, ask_order, False)
			util.process_trades(trades, traders, ask_order, cur_time)
			# sent bid order to exchange
			trades = exchange.process_order(cur_time, bid_order, False)
			util.process_trades(trades, traders, bid_order, cur_time)

		# liquidity consumer
		# print("liquidity consumer")
		if cur_time == 0:
			# initialize internal parameters at start of day
			liquidity_consumer.make_decision()
		order = liquidity_consumer.work(exchange, cur_time)
		# print(order)
		if order is not None:
			trades = exchange.process_order(cur_time, order, False)
			util.process_trades(trades, traders, order, cur_time)

		# momentum trader
		# print("momentum trader")
		order = momentum_trader.work(exchange, cur_time)
		# print(order)
		if order is not None:
			trades = exchange.process_order(cur_time, order, False)
			util.process_trades(trades, traders, order, cur_time)

		# mean reversion trader
		# print("mean reversion trader")
		order = mean_reversion_trader.work(exchange, cur_time)
		# print(order)
		if order is not None:
			trades = exchange.process_order(cur_time, order, False)
			util.process_trades(trades, traders, order, cur_time)

		# noise trader
		# print("noise trader")
		order = noise_trader.work(exchange, cur_time)
		# print(order)
		if order is not None:
			trades = exchange.process_order(cur_time, order, False)
			util.process_trades(trades, traders, order, cur_time)
		logger.debug(exchange.price)
		cur_time += 1
	# pprint(exchange.tape)

	exchange.tape_dump(os.path.join(data_dir, "transaction_records.csv"), "w", "keep")
	exchange.orders_dump(os.path.join(data_dir, "orders.csv"), "w")

	# util.plot_price_trend(exchange, 500)
	# prices = util.sample_data(exchange.all_deal_prices, 50)
	plt.plot(exchange.all_deal_prices)
	plt.show()


if __name__ == "__main__":
	main()
