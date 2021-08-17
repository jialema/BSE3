import math
from functools import reduce
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import kurtosis
import statsmodels.tsa.api as smt


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


def find_price_spike(all_deal_prices, up_or_down_times=5, rate=0.0001, init_price=100):
	results = []
	last_price = init_price
	up_times = 0
	down_times = 0
	for i in range(len(all_deal_prices)):
		cur_price = all_deal_prices[i]
		if cur_price - last_price >= init_price * rate:
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
		elif last_price - cur_price > init_price * rate:
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
	return results


def sample_data(data, number):
	span = len(data) // number
	result = []
	temp = []
	init_span = span
	for i in range(len(data)):
		if i < span:
			temp.append(data[i])
		else:
			span = span + init_span
			result.append(sum(temp) / len(temp))
			temp = [data[i]]
	if temp:
		result.append(sum(temp) / len(temp))
	# print("sample_data length: ", len(result))
	return result[1:]


def concave_price_impact(exchange):
	mid_quotes = exchange.mid_quotes
	price_impacts = []
	order_quantities = []
	for i in range(1, len(mid_quotes)):
		price_impact = mid_quotes[i]["mid_quote"] - mid_quotes[i - 1]["mid_quote"]
		if price_impact == 0:
			continue
		price_impacts.append(math.log10(abs(price_impact)))
		order_quantities.append(mid_quotes[i]["quantity"])
	max_quantity = max(order_quantities)
	min_quantity = min(order_quantities)
	print(max_quantity, min_quantity)
	normalized_quantities = [(x - min_quantity) / (max_quantity - min_quantity) for x in order_quantities]
	plt.plot(sample_data(price_impacts, 10))
	# plt.scatter(normalized_quantities, price_impacts)
	plt.show()


def volatility_clustering(exchange):
	all_deal_prices = exchange.all_deal_prices
	y = []
	cur_total_price = 0
	for price in all_deal_prices:
		cur_total_price += price - 100
		y.append(cur_total_price)

	acf = auto_correlation(y, 1)
	print(acf[0], acf[-1])
	plt.show()


def fat_tailed_distribution(exchange):
	mid_quotes = exchange.mid_quotes
	time_scales = list(range(500, 5000, 500))
	kurtosis_multi_scales = []
	for time_scale in time_scales:
		mid_quote_returns = []
		for i in range(len(mid_quotes) - time_scale):
			mid_quote_return = math.log(mid_quotes[i + time_scale]["mid_quote"] / mid_quotes[i]["mid_quote"])
			mid_quote_returns.append(mid_quote_return)
		kurt = kurtosis(mid_quote_returns)
		kurtosis_multi_scales.append(kurt)
	plt.plot([e["mid_quote"] for e in mid_quotes])
	plt.show()
	plt.plot(time_scales, kurtosis_multi_scales)
	plt.show()


def return_auto_correlation_statistics(exchange):
	mid_quotes = exchange.mid_quotes
	time_scales = list(range(500, 5000, 500))
	acf_multi_scales = []
	for time_scale in time_scales:
		mid_quote_returns = []
		for i in range(len(mid_quotes) - time_scale):
			mid_quote_return = math.log10(mid_quotes[i + time_scale]["mid_quote"] / mid_quotes[i]["mid_quote"])
			mid_quote_returns.append(mid_quote_return)

		acf = auto_correlation(mid_quote_returns, 1)
		acf_multi_scales.append(acf[0])
	mid_prices = [e["mid_quote"] for e in mid_quotes]
	plt.plot(mid_prices)
	mid_prices_mean = pd.DataFrame.ewm(pd.Series(mid_prices), span=1000).mean()
	plt.plot(mid_prices_mean)
	plt.title("mid-price")
	plt.show()
	print("acf on different scales: {}".format(acf_multi_scales))

	# trade_prices = exchange.all_deal_prices
	# time_scales = list(range(500, 1000, 500))
	# acf_multi_scales = []
	# for time_scale in time_scales:
	# 	trade_price_returns = []
	# 	for i in range(len(trade_prices) - time_scale):
	# 		trade_price_return = math.log10(trade_prices[i + time_scale] / trade_prices[i])
	# 		trade_price_returns.append(trade_price_return)
	# 	roll_weighted_mean = pd.DataFrame.ewm(pd.Series(trade_price_returns), span=100).mean()
	# 	# df = pd.DataFrame(trade_price_returns)
	# 	# acf = smt.stattools.acf(df, nlags=1)
	# 	acf = auto_correlation(trade_price_returns, 10)
	# 	acf_mean = auto_correlation(trade_price_returns, 10)
	# 	print(acf_mean)
	# 	acf_multi_scales.append(acf[0])
	#
	# 	plt.plot(trade_price_returns, label="time_scales:{}".format(time_scale))
	# 	plt.plot(roll_weighted_mean, label="time_scales:{}".format(time_scale))
	# plt.title("acf_trade_price_returns")
	# plt.show()
	# print("acf on different scales: {}".format(acf_multi_scales))

