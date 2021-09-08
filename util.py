import sys
import logging
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import math


def create_log(file_name):
	logger = logging.getLogger("logger")
	logger.setLevel(logging.DEBUG)

	file_handler = logging.FileHandler(file_name, "w", encoding='utf-8')
	file_handler.setLevel(logging.DEBUG)

	stream_handler = logging.StreamHandler()
	stream_handler.setLevel(logging.INFO)

	formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
	file_handler.setFormatter(formatter)
	stream_handler.setFormatter(formatter)

	logger.addHandler(file_handler)
	logger.addHandler(stream_handler)
	return logger


def process_trades(trades, traders, order, cur_time):
	for trade in trades:
		if trade is not None:
			# trade occurred so the counterparties update order lists and blotters
			traders[trade["ask"]].book_keep(trade, order, cur_time)
			traders[trade["bid"]].book_keep(trade, order, cur_time)


def sample_data(data, times, number):
	sampled_data = []
	temp = []
	# sample data according to number
	# for i in range(len(data)):
	# 	temp.append(data[i])
	# 	if i % number == 0:
	# 		sampled_data.append(sum(temp) / len(temp))
	# 		temp = []

	# sample data according to time span
	inx = 1
	for i in range(len(data)):
		temp.append(data[i])
		if times[i] > number * inx:
			sampled_data.append(sum(temp) / len(temp))
			temp = []
			inx += 1
	return sampled_data


def plot_price_trend(exchange):
	print("all prices: {}".format(len(exchange.prices)))
	trade_price_rolling_mean = pd.DataFrame.ewm(pd.Series(exchange.prices), span=2000).mean()
	plt.figure(figsize=(8, 4))
	plt.plot(exchange.prices)
	plt.plot(trade_price_rolling_mean)
	plt.title("Price Trend")
	plt.xlabel("Period")
	plt.ylabel("Price")
	plt.legend()
	plt.savefig("figures/price trend up 100.png", dpi=400, bbox_inches='tight')
	plt.show()
	exchange.trade_price_rolling_mean = trade_price_rolling_mean

def plot_order_scatter(agent_order):
	bids = {"price": [], "quantity": []}
	asks = {"price": [], "quantity": []}
	for bid_order in agent_order["bids"]:
		bids["price"].append(bid_order.price)
		bids["quantity"].append(bid_order.quantity)

	for ask_order in agent_order["asks"]:
		asks["price"].append(ask_order.price)
		asks["quantity"].append(ask_order.quantity)

	plt.figure()
	plt.scatter(bids["quantity"], bids["price"])
	plt.show()

def get_code_position():
	position = "File \"{}\", line {}, in {}".format(
		sys._getframe().f_code.co_filename,
		sys._getframe().f_lineno,
		sys._getframe().f_code.co_name)
	return position
