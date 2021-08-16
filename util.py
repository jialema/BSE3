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


def plot_price_trend(exchange, number):
	prices = []
	temp = []
	inx = 1
	for tape_item in exchange.tape:
		if tape_item["type"] == "Trade":
			if tape_item["time"] < inx * number:
				temp.append(tape_item["price"])
			else:
				prices.append(sum(temp)/len(temp))
				temp = [tape_item["price"]]
				inx += 1
	plt.plot(prices)
	plt.show()


def get_code_position():
	position = "File \"{}\", line {}, in {}".format(
		sys._getframe().f_code.co_filename,
		sys._getframe().f_lineno,
		sys._getframe().f_code.co_name)
	return position
