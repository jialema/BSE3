import time
from order import Order


class Trader:
	def __init__(self):
		# trader ID code
		self.trader_id = ""
		# record of trades executed
		self.blotter = []
		# wealth
		self.wealth = 0

	def buy(self, bid_price, quantity, cur_time):
		if bid_price is None or quantity is None:
			return None
		bid_price = round(bid_price, 2)
		order = Order(trader_id=self.trader_id, order_type="Bid", price=bid_price, quantity=quantity, time=cur_time)
		return order

	def sell(self, ask_price, quantity, cur_time):
		if ask_price is None or quantity is None:
			return None
		ask_price = round(ask_price, 2)
		order = Order(trader_id=self.trader_id, order_type="Ask", price=ask_price, quantity=quantity, time=cur_time)
		return order

	def book_keep(self, trade, order, cur_time):
		self.blotter.append(trade)
		deal_price = trade["price"]
		if order.order_type == "Bid":
			self.wealth -= deal_price
		else:
			self.wealth += deal_price

	def __str__(self):
		return self.trader_id
