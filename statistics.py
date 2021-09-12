import copy
import math
from functools import reduce
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import kurtosis
import statsmodels.tsa.api as smt
import sys
import random
import uuid


def auto_correlation(x, lags):
	"""
	Calculate the auto correlation coefficient within lags order, return lags values, and
	calculate the sequence mean and standard deviation respectively.
	:param x: time series
	:param lags: logs
	:return: auto correction coefficient
	"""
	n = len(x)
	x = np.array(x)
	result = []
	for i in range(1, lags + 1):
		y = abs(np.correlate(x[i:] - x[i:].mean(), x[:n - i] - x[:n - i].mean())[0])
		d = (x[i:].std() * x[:n - i].std() * (n - i))
		result.append(y / d)
	return result


def hurst(data):
	"""
	Compute the hurst exponent of input data.
	:param data: time series
	:return: the value of hurst exponent
	"""
	n = 6
	data = pd.Series(data).pct_change()[1:]
	ars = list()
	lag = list()
	for i in range(n):
		m = 2 ** i
		size = np.size(data) // m
		lag.append(size)
		panel = {}
		for j in range(m):
			panel[str(j)] = data[j * size:(j + 1) * size].values

		panel = pd.DataFrame(panel)
		mean = panel.mean()
		deviation = (panel - mean).cumsum()
		maxi = deviation.max()
		mini = deviation.min()
		sigma = panel.std()
		rs = maxi - mini
		rs = rs / sigma
		ars.append(rs.mean())

	lag = np.log10(lag)
	ars = np.log10(ars)
	hurst_exponent = np.polyfit(lag, ars, 1)
	result = hurst_exponent[0]
	return result


def long_memory_in_order_flow(exchange):
	ac = auto_correlation(exchange.orders_signs, 1)
	h = hurst(exchange.orders_signs)
	print("Auto-correlation: {}".format(ac))
	print("Hurst: {}".format(h))


def price_spike_example():
	prices = [100+random.random()/300 for i in range(100)]
	for i in range(20):
		price = prices[-1] + random.randint(8, 10) / 1000 + random.random()/300
		prices.append(price)
	for i in range(10):
		price = prices[-1] - random.randint(8, 10) / 1000 + random.random()/300
		prices.append(price)
	price = prices[-1]
	for i in range(100):
		prices.append(price + random.random()/300)
	plt.figure(figsize=(8,4))
	plt.scatter(list(range(len(prices))), prices)
	plt.savefig("figures/price spike example {}.png".format(uuid.uuid4()), dpi=400, bbox_inches="tight")
	plt.show()


def find_price_spike(exchange, up_or_down_times=5, rate=0.00001):
	all_prices = exchange.all_deal_prices
	results = []
	last_price = exchange.init_price
	up_times = 0
	down_times = 0
	for i in range(len(all_prices)):
		cur_price = all_prices[i]
		if cur_price - last_price >= exchange.init_price * rate:
			if down_times == 0:
				up_times += 1
			else:
				if down_times >= up_or_down_times:
					first_tick = i - down_times - 1
					last_tick = i - 1
					tick_span = {
						"first_tick": first_tick,
						"last_tick": last_tick,
					}
					results.append(tick_span)
				down_times = 0
				up_times = 1
		elif last_price - cur_price > exchange.init_price * rate:
			if up_times == 0:
				down_times += 1
			else:
				if up_times >= up_or_down_times:
					first_tick = i - up_times - 1
					last_tick = i - 1
					tick_span = {
						"first_tick": first_tick,
						"last_tick": last_tick,
					}
					results.append(tick_span)
				up_times = 0
				down_times = 1
		else:
			up_times = 0
			down_times = 0

		last_price = cur_price
	print(results)


def sample_data(data, quantity):
	threshold = 10
	i = 0
	temp = []
	result1 = []
	result2 = []
	while i < len(data):
		if quantity[i] < threshold:
			temp.append(data[i])
		else:
			if temp:
				result1.append(sum(temp) / len(temp))
			else:
				result1.append(0)
			result2.append(threshold)
			threshold *= 10
			temp = []
		i += 1
	if temp:
		result1.append(sum(temp))
		result2.append(threshold)
	print(result1[1:], result2[1:])
	return result1[1:], result2[1:]


def concave_price_impact(exchange):
	mid_quotes = exchange.mid_quotes
	price_impacts = []
	order_quantities = []
	for i in range(1, len(mid_quotes)):
		price_impact = mid_quotes[i - 1]["mid_quote"] / mid_quotes[i]["mid_quote"]
		if price_impact == 0:
			continue
		price_impacts.append(math.log(price_impact))
		order_quantities.append(mid_quotes[i]["quantity"])

	# plt.plot(sample_data(price_impacts, 10))
	price_quantity_pairs = []
	for i in range(len(price_impacts)):
		price_quantity_pairs.append([price_impacts[i], order_quantities[i]])
	price_quantity_sorted = sorted(price_quantity_pairs, key=lambda d: d[1])
	price_impacts_sorted = [e[0] for e in price_quantity_sorted]
	quantities_sorted = [e[1] for e in price_quantity_sorted]
	# price_impacts_sorted = pd.DataFrame.ewm(pd.Series(price_impacts_sorted), span=500).mean()
	plt.figure(figsize=(8, 4))
	result1, result2 = sample_data(price_impacts_sorted, quantities_sorted)
	plt.plot(result2, result1)
	plt.xlabel("Trade size")
	plt.ylabel("Price impact")
	plt.savefig("figures/concave price impact {}.png".format(uuid.uuid4()), dpi=400, bbox_inches="tight")
	plt.show()


def volatility_clustering(exchange):
	mid_prices = exchange.mid_quotes
	time_scales = list(range(1, 2000, 10))
	hursts = []
	for time_scale in time_scales:
		mid_price_returns = []
		for i in range(len(mid_prices) - time_scale):
			mid_price_return = math.log(mid_prices[i + time_scale]["mid_quote"] / mid_prices[i]["mid_quote"])
			mid_price_returns.append(abs(mid_price_return))
		y = []
		cur_total_price = 0
		for price in mid_price_returns:
			cur_total_price += price
			y.append(price)
		acfs = auto_correlation(y, 1)
		h = math.log(acfs[-1], 5)
		hursts.append(abs(h) * 100)
	plt.plot(time_scales, hursts)
	plt.xlabel("Time-scale")
	plt.ylabel("% Volatility clustering")
	plt.savefig("figures/volatility_clustering.png", dpi=400, bbox_inches="tight")
	plt.show()


def fat_tailed_distribution(exchange):
	mid_prices = exchange.mid_prices
	time_scales = list(range(500, 50000, 500))
	kurtosis_multi_scales = []
	for time_scale in time_scales:
		mid_quote_returns = []
		for i in range(len(mid_prices) - time_scale):
			mid_quote_return = math.log(mid_prices[i + time_scale] / mid_prices[i])
			mid_quote_returns.append(mid_quote_return)
		kurt = kurtosis(mid_quote_returns)
		kurtosis_multi_scales.append(kurt)
	plt.figure(figsize=(8, 4))
	# plt.plot(mid_prices)
	mid_price_rolling_mean = pd.DataFrame.ewm(pd.Series(mid_prices), span=2000).mean()
	plt.plot(mid_price_rolling_mean)
	plt.xlabel("Period")
	plt.ylabel("Mid-price")
	plt.savefig("figures/mid-price-{}.png".format(str(uuid.uuid4())), dpi=400, bbox_inches="tight")
	plt.show()

	plt.figure(figsize=(8, 4))
	plt.plot(time_scales, kurtosis_multi_scales)
	plt.xlabel("Time-scale")
	plt.ylabel("Kurtosis")
	plt.savefig("figures/fat-tailed-distribution-{}.png".format(str(uuid.uuid4())), dpi=400, bbox_inches="tight")
	plt.show()


def return_auto_correlation(exchange):
	mid_prices = exchange.mid_prices
	time_scales = list(range(1, 10))
	for time_scale in time_scales:
		mid_price_returns = []
		for i in range(len(mid_prices) - time_scale):
			mid_price_return = math.log(mid_prices[i + time_scale] / mid_prices[i])
			mid_price_returns.append(mid_price_return)
		acfs = auto_correlation(mid_price_returns, 10)
		print(acfs)
	# plt.plot(time_scales, hursts)
	# plt.xlabel("Time-scale")
	# plt.ylabel("% Volatility clustering")
	# plt.savefig("figures/volatility_clustering.png", dpi=400, bbox_inches="tight")
	# plt.show()

	print()
	trade_prices = exchange.prices
	trade_prices = pd.DataFrame.ewm(pd.Series(trade_prices), span=4).mean()

	acf_multi_scales = []
	for time_scale in time_scales:
		trade_price_returns = []
		for i in range(len(trade_prices) - time_scale):
			mid_quote_return = math.log(trade_prices[i + time_scale]) - math.log(trade_prices[i])
			trade_price_returns.append(mid_quote_return)
		acfs = auto_correlation(trade_price_returns, 10)
		print(acfs)
	#
	# print("acf on different scales: {}".format(acf_multi_scales))
