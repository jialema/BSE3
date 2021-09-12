import sys
import logging
import pandas as pd
import matplotlib.pyplot as plt
import uuid
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
	# plt.plot(exchange.prices)
	plt.plot(trade_price_rolling_mean)
	plt.title("Price Trend")
	plt.xlabel("Period")
	plt.ylabel("Price")
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


def plot_order_proportion(exchange):
	all_trade_record = exchange.tape
	total_quantity = 0
	mm_quantity = 0
	lc_quantity = 0
	mr_quantity = 0
	mt_quantity = 0
	nt_quantity = 0
	lc_last = 0
	for trade in all_trade_record:
		if trade["type"] == "Trade":
			total_quantity += trade["quantity"]
			if trade["ask"] == "market maker" or trade["bid"] == "market maker":
				mm_quantity += trade["quantity"]
			if trade["ask"] == "liquidity consumer" or trade["bid"] == "liquidity consumer":
				lc_quantity += trade["quantity"]
				lc_last = trade["time"]
			if trade["ask"] == "mean reversion trader" or trade["bid"] == "mean reversion trader":
				mr_quantity += trade["quantity"]
			if trade["ask"] == "momentum trader" or trade["bid"] == "momentum trader":
				mt_quantity += trade["quantity"]
			if trade["ask"] == "noise trader" or trade["bid"] == "noise trader":
				nt_quantity += trade["quantity"]

	# for trade in all_trade_record:
	# 	if trade["type"] == "Trade":
	# 		total_quantity += trade["quantity"]
	# 		if trade["ask"] == "market maker":
	# 			mm_quantity += trade["quantity"]
	# 		if trade["ask"] == "liquidity consumer":
	# 			lc_quantity += trade["quantity"]
	# 		if trade["ask"] == "mean reversion trader":
	# 			mr_quantity += trade["quantity"]
	# 		if trade["ask"] == "momentum trader":
	# 			mt_quantity += trade["quantity"]
	# 		if trade["ask"] == "noise trader":
	# 			nt_quantity += trade["quantity"]
	#
	# 		if trade["bid"] == "market maker":
	# 			mm_quantity += trade["quantity"]
	# 		if trade["bid"] == "liquidity consumer":
	# 			lc_quantity += trade["quantity"]
	# 		if trade["bid"] == "mean reversion trader":
	# 			mr_quantity += trade["quantity"]
	# 		if trade["bid"] == "momentum trader":
	# 			mt_quantity += trade["quantity"]
	# 		if trade["bid"] == "noise trader":
	# 			nt_quantity += trade["quantity"]
	print(lc_last)
	print(total_quantity)
	print(mm_quantity, lc_quantity, mr_quantity, mt_quantity, nt_quantity)
	# total_quantity = mm_quantity + lc_quantity + mr_quantity + mt_quantity + nt_quantity
	# print(total_quantity)
	ranges = ["noise\ntraders", "others"]
	plt.pie([nt_quantity, total_quantity-nt_quantity], labels=ranges, autopct="%1.2f%%")
	plt.savefig("figures/noise trader order proportion.png", dpi=400, bbox_inches='tight')
	plt.show()


def plot_order_hist(exchange):
	all_trade_record = exchange.tape
	quantities = []
	for trade in all_trade_record:
		if trade["type"] == "Trade":
			quantities.append(trade["price"])
	import scipy
	mu = np.mean(quantities)
	sigma = np.std(quantities)
	num_bins = 100
	n, bins, patches = plt.hist(quantities, num_bins, density=1)
	y = scipy.stats.norm.pdf(bins, mu, sigma)

	# plt.figure()
	# plt.hist(quantities, bins=100)
	plt.plot(bins, y)
	plt.xlabel("Price")
	plt.ylabel("Probability")
	plt.savefig("figures/hist"+str(uuid.uuid4())+".png", dpi=400, bbox_inches="tight")
	plt.show()


def get_code_position():
	position = "File \"{}\", line {}, in {}".format(
		sys._getframe().f_code.co_filename,
		sys._getframe().f_lineno,
		sys._getframe().f_code.co_name)
	return position
