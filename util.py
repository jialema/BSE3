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
	print("all trade prices: {}".format(len(exchange.all_deal_prices)))
	trade_price_rolling_mean = pd.DataFrame.ewm(pd.Series(exchange.all_deal_prices), span=100).mean()
	# plt.plot(exchange.all_deal_prices)
	plt.plot(trade_price_rolling_mean)
	plt.title("trade price trend")
	plt.show()
	exchange.trade_price_rolling_mean = trade_price_rolling_mean


def get_code_position():
	position = "File \"{}\", line {}, in {}".format(
		sys._getframe().f_code.co_filename,
		sys._getframe().f_lineno,
		sys._getframe().f_code.co_name)
	return position
