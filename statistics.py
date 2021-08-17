import copy
import math
from functools import reduce
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import kurtosis
import statsmodels.tsa.api as smt
import sys


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


def return_auto_correlation(exchange):
	# remove duplicates
	mid_quotes_re = []
	for i in range(len(exchange.mid_quotes)):
		if mid_quotes_re and mid_quotes_re[-1]["time"] == exchange.mid_quotes[i]["time"]:
			mid_quotes_re[-1]["mid_quote"] = (mid_quotes_re[-1]["mid_quote"] + exchange.mid_quotes[i]["mid_quote"]) / 2
			mid_quotes_re[-1]["quantity"] = mid_quotes_re[-1]["quantity"] + exchange.mid_quotes[i]["quantity"]
		else:
			mid_quotes_re.append(copy.deepcopy(exchange.mid_quotes[i]))

	# fill the blank time
	mid_quotes = []
	i = 0
	j = 0
	last_mid_quote = 100
	while i < 200000 or j < len(mid_quotes_re):
		if j == len(mid_quotes_re) or i < mid_quotes_re[j]["time"]:
			# mid_quotes.append([i, last_mid_quote])
			mid_quotes.append([i, 0])
			i += 1
		elif i == mid_quotes_re[j]["time"]:
			mid_quotes.append([i, mid_quotes_re[j]["mid_quote"]])
			last_mid_quote = mid_quotes_re[j]["mid_quote"]
			i += 1
			j += 1
		else:
			sys.exit("[Error] bad i or j value")

	# show the trend
	# mid_prices = [e[1] for e in mid_quotes]
	# plt.plot(mid_prices)
	# mid_prices_mean = pd.DataFrame.ewm(pd.Series(mid_prices), span=1000).mean()
	# plt.plot(mid_prices_mean)
	# plt.title("Mid-quote trend")
	# plt.show()

	# compute the return auto correlation
	time_scales = list(range(500, 5000, 500))
	acf_multi_scales = []
	for time_scale in time_scales:
		mid_quote_returns = []
		for i in range(len(mid_quotes) - time_scale):
			try:
				mid_quote_return = math.log(mid_quotes[i + time_scale][1]) - math.log(mid_quotes[i][1])
			except ValueError:
				mid_quote_return = 0
			mid_quote_returns.append(mid_quote_return)
		# plt.plot(mid_quote_returns)
		# plt.title("mid-quote return on {}".format(time_scale))
		# plt.show()
		# rolling_mean = pd.DataFrame.ewm(pd.Series(mid_quote_returns), span=3000).mean()
		acf = auto_correlation(mid_quote_returns, 1)
		acf_multi_scales.append(acf[0])

		# plt.plot(mid_quote_returns)
		# plt.title("mid-quote return on timescale {}".format(time_scale))
		# plt.show()

	print("acf on different scales: {}".format(acf_multi_scales))

	#
	trade_prices_re = []
	for i in range(len(exchange.tape)):
		trade = exchange.tape[i]
		if trade["type"] == "Trade":
			if trade_prices_re and trade_prices_re[-1]["time"] == trade["time"]:
				trade_prices_re[-1]["price"] = (trade_prices_re[-1]["price"] * trade_prices_re[-1]["quantity"] + trade["price"] * trade["quantity"]) / (trade_prices_re[-1]["quantity"] + trade["quantity"])
				trade_prices_re[-1]["quantity"] = trade_prices_re[-1]["quantity"] + trade["quantity"]
			else:
				trade_prices_re.append({
					"time": trade["time"],
					"price": trade["price"],
					"quantity": trade["quantity"]
				})

	# fill the blank time
	trade_prices = []
	i = 0
	j = 0
	last_trade_price = 100
	while i < 200000 or j < len(trade_prices_re):
		if j == len(trade_prices_re) or i < trade_prices_re[j]["time"]:
			# trade_prices.append([i, last_trade_price])
			trade_prices.append([i, (last_trade_price * 1.75 + 100)/2.75])
			i += 1
		elif i == trade_prices_re[j]["time"]:
			trade_prices.append([i, trade_prices_re[j]["price"]])
			last_trade_price = trade_prices_re[j]["price"]
			i += 1
			j += 1
		else:
			sys.exit("[Error] bad i or j value")

	acf_multi_scales = []
	for time_scale in time_scales:
		trade_price_returns = []
		for i in range(len(trade_prices) - time_scale):
			try:
				trade_price_return = math.log(trade_prices[i + time_scale][1]) - math.log(trade_prices[i][1])
			except ValueError:
				trade_price_return = 0
			trade_price_returns.append(trade_price_return)
		acf = auto_correlation(trade_price_returns, 1)
		acf_multi_scales.append(acf[0])

	print("acf on different scales: {}".format(acf_multi_scales))
