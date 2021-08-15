import sys
from order import Order
from order_book import OrderBook
import time
import copy


class Exchange(OrderBook):

	def __init__(self, init_price=100, init_spread=0.05, tick_size=0.01):
		super().__init__()
		# newest deal price
		self.price = init_price
		self.all_deal_prices = []
		# price spread
		self.spread = init_spread
		# minimum size of price change
		self.tick_size = tick_size
		self.all_orders_for_record = []

	def add_order(self, order):
		"""
		add a quote/order to the exchange and update all internal records; return unique i.d.
		@param order: order, the instance of the class Order
		@return:
		"""
		order.quote_id = self.quote_id
		self.quote_id += 1
		if order.order_type == 'Bid':
			response = self.bids.book_add(order)
			best_price = self.bids.lob_anon[-1][0]
			self.bids.best_price = best_price
			self.bids.best_trader_id = self.bids.lob[best_price][1][0][2]
		else:
			response = self.asks.book_add(order)
			best_price = self.asks.lob_anon[0][0]
			self.asks.best_price = best_price
			self.asks.best_trader_id = self.asks.lob[best_price][1][0][2]
		return [order.quote_id, response]

	def del_trader_all_orders(self, trader_id, cur_time):
		"""
		delete any existing orders from a certain trader
		@param trader_id: ID of a certain trader, like market maker
		@param cur_time: current time
		"""
		if trader_id in self.bids.orders:
			self.bids.book_del(trader_id)
			cancel_record = {'type': 'Cancel', 'time': cur_time, 'trader_id': trader_id}
			self.tape.append(cancel_record)
		if trader_id in self.asks.orders:
			self.asks.book_del(trader_id)
			cancel_record = {'type': 'Cancel', 'time': cur_time, 'trader_id': trader_id}
			self.tape.append(cancel_record)

	def del_order(self, order_time, order):
		"""
		delete a trader's quot/order from the exchange, update all internal records
		@param order_time:
		@param order:
		@return:
		"""
		if order.order_type == 'Bid':
			self.bids.book_del(order.train_id)
			cancel_record = {'type': 'Cancel', 'time': order_time, 'order': order}
			self.tape.append(cancel_record)
		elif order.order_type == 'Ask':
			self.asks.book_del(order.train_id)
			cancel_record = {'type': 'Cancel', 'time': order_time, 'order': order}
			self.tape.append(cancel_record)
		else:
			# neither bid nor ask?
			sys.exit('bad order type in del_quote()')

	def make_match(self, order, cur_time):
		if self.asks.best_quantity is None or self.bids.best_quantity is None:
			return None
		best_ask_price = self.asks.best_price
		best_ask_trader_id = self.asks.best_trader_id
		best_bid_price = self.bids.best_price
		best_bid_trader_id = self.bids.best_trader_id

		if best_bid_price >= best_ask_price:
			if order.order_type == "Bid":
				price = best_ask_price
			elif order.order_type == "Ask":
				price = best_bid_price
			else:
				sys.exit("[Error] bad order.order_type value")
			quantity = min(self.asks.best_quantity, self.bids.best_quantity)
			transaction_record = {
				'type': 'Trade',
				'time': cur_time,
				'price': price,
				'ask': best_ask_trader_id,
				'bid': best_bid_trader_id,
				'quantity': quantity
			}
			self.asks.delete_best(quantity)
			self.bids.delete_best(quantity)
			self.tape.append(transaction_record)
			self.all_deal_prices.append(price)
			self.price = price
			return transaction_record
		return None

	def process_order(self, cur_time, order, verbose):
		[quote_id, response] = self.add_order(order)
		order.quote_id = quote_id
		self.all_orders_for_record.append(copy.deepcopy(order))
		trades = []
		while True:
			trade = self.make_match(order, cur_time)
			if trade is not None:
				trades.append(trade)
			else:
				break
		return trades

	def publish_lob(self, cur_time, verbose):
		"""
		this returns the LOB data "published" by the exchange,
		i.e., what is accessible to the traders
		"""
		public_data = dict()
		public_data['time'] = cur_time
		public_data['bids'] = {
			'best': self.bids.best_price,
			'worst': self.bids.worstprice,
			'n': self.bids.number_traders,
			'lob': self.bids.lob_anon}
		public_data['asks'] = {
			'best': self.asks.best_price,
			'worst': self.asks.worstprice,
			'sess_hi': self.asks.session_extreme,
			'n': self.asks.number_traders,
			'lob': self.asks.lob_anon}
		public_data['quote_id'] = self.quote_id
		public_data['tape'] = self.tape
		if verbose:
			print('publish_lob: t=%d' % cur_time)
			print('BID_lob=%s' % public_data['bids']['lob'])
			print('ASK_lob=%s' % public_data['asks']['lob'])

		return public_data

	def tape_dump(self, file_name, file_mode, tape_mode):
		"""
		Currently tape_dump only writes a list of transactions
		"""
		dump_file = open(file_name, file_mode)
		for tape_item in self.tape:
			if tape_item["type"] == "Trade":
				dump_file.write("type: {}, time: {}, bid: {}, ask: {}, price: {}, quantity: {}\n".format(
					tape_item["type"],
					tape_item["time"],
					tape_item["bid"],
					tape_item["ask"],
					tape_item["price"],
					tape_item["quantity"]
				))
			elif tape_item["type"] == "Cancel":
				dump_file.write("type: {}, time: {}, trader_id: {}\n".format(
					tape_item["type"],
					tape_item["time"],
					tape_item["trader_id"]
				))
		dump_file.close()
		if tape_mode == "wipe":
			self.tape = []

	def orders_dump(self, file_name, file_mode):
		dump_file = open(file_name, file_mode)
		for order in self.all_orders_for_record:
			dump_file.write("time: {}, order_type: {}, trade_id: {}, price: {}, quantity: {}, quote_id: {}\n".format(
				order.time,
				order.order_type,
				order.trader_id,
				order.price,
				order.quantity,
				order.quote_id
			))
		dump_file.close()

	def __str__(self):
		return "exchange"
