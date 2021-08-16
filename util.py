import sys
import logging

import matplotlib.pyplot as plt
import numpy as np


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


def sample_data(data, number):
	sampled_data = []
	temp = []
	for i in range(len(data)):
		temp.append(data[i])
		if i % number == 0:
			sampled_data.append(sum(temp) / len(temp))
			temp = []
	return sampled_data


def plot_price_trend(exchange):
	times = []
	prices = []
	price = 0
	quantity = 0
	last_time = -1
	for tape_item in exchange.tape:
		if tape_item["type"] == "Trade":
			cur_time = tape_item["time"]
			if cur_time == last_time:
				price += tape_item["price"] * tape_item["quantity"]
				quantity += tape_item["quantity"]
			else:
				if quantity != 0:
					times.append(cur_time)
					prices.append(round(price / quantity, 2))
				price = tape_item["price"] * tape_item["quantity"]
				quantity = tape_item["quantity"]

			last_time = cur_time

	plt.plot(sample_data(prices, 50))
	plt.show()
	plt.plot(times, prices)
	plt.show()


def get_code_position():
	position = "File \"{}\", line {}, in {}".format(
		sys._getframe().f_code.co_filename,
		sys._getframe().f_lineno,
		sys._getframe().f_code.co_name)
	return position
