import sys
from order import Order
from order_book import OrderBook
import time


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

	def del_any_existing_orders_by_trader(self, trader_id, cur_time):
		"""
		delete any existing orders from a certain trader
		@param trader_id: ID of a certain trader, like market maker
		@param cur_time: current time
		"""
		if self.bids.orders.contain(trader_id):
			self.bids.book_del(trader_id)
			cancel_record = {'type': 'Cancel', 'time': cur_time, 'trader_id': trader_id}
			self.tape.append(cancel_record)
		if self.asks.orders.contains(trader_id):
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

	def make_match(self, cur_time, order, verbose):
		trades = []
		if order.quantity == 1:
			trade = self.process_order(cur_time, order, verbose)
			trades.append(trade)
		else:
			# split order
			for i in range(order.quantity):
				order_with_quantity_one = Order(order.trader_id, order.order_type, order.price, order.quantity, order.time)
				trade = self.process_order(cur_time, order_with_quantity_one, verbose)
				trades.append(trade)
		return trades

	def process_order(self, cur_time, order, verbose):
		"""
		receive an order and either add it to the relevant LOB (ie treat as limit order)
		or if it crosses the best counterparty offer, execute it (treat as a market order)
		NB this function can only process the order with quantity one.
		"""
		order_price = order.price
		counterparty = None
		# add it to the order lists and overwrite any previous order
		[quote_id, response] = self.add_order(order, verbose)
		order.quote_id = quote_id
		if verbose:
			print('QUID: order.quid=%d' % order.quote_id)
			print('RESPONSE: %s' % response)
		best_ask = self.asks.best_price
		best_ask_trader_id = self.asks.best_trader_id
		best_bid = self.bids.best_price
		best_bid_trader_id = self.bids.best_trader_id
		if order.order_type == 'Bid':
			if self.asks.number_orders > 0 and best_bid >= best_ask:
				# bid lifts the best ask
				if verbose:
					print("Bid $%s lifts best ask" % order_price)
				counterparty = best_ask_trader_id
				# bid crossed ask, so use ask price
				price = best_ask
				if verbose:
					print('counterparty, price', counterparty, price)
				# delete the ask just crossed
				self.asks.delete_best()
				# delete the bid that was the latest order
				self.bids.delete_best()
		elif order.order_type == 'Ask':
			if self.bids.number_orders > 0 and best_ask <= best_bid:
				# ask hits the best bid
				if verbose:
					print("Ask $%s hits best bid" % order_price)
				# remove the best bid
				counterparty = best_bid_trader_id
				# ask crossed bid, so use bid price
				price = best_bid
				if verbose:
					print('counterparty, price', counterparty, price)
				# delete the bid just crossed, from the exchange's records
				self.bids.delete_best()
				# delete the ask that was the latest order, from the exchange's records
				self.asks.delete_best()
		else:
			# we should never get here
			sys.exit('process_order() given neither Bid nor Ask')
		"""
		NB at this point we have deleted the order from the exchange's records
		but the two traders concerned still have to be notified
		"""
		if verbose:
			print('counterparty %s' % counterparty)
		if counterparty is not None:
			# process the trade
			if verbose:
				print('>>>>>>>>>>>>>>>>>TRADE t=%010.3f $%d %s %s' % (cur_time, price, counterparty, order.trader_id))
			transaction_record = {
				'type': 'Trade',
				'time': cur_time,
				'price': price,
				'party1': counterparty,
				'party2': order.trader_id,
				'quantity': order.quantity
			}
			self.tape.append(transaction_record)
			self.all_deal_prices.append(price)
			self.price = price
			return transaction_record
		else:
			return None

	def tape_dump(self, file_name, file_mode, tape_mode):
		"""
		Currently tape_dump only writes a list of transactions (ignores cancellations)
		"""
		dumpfile = open(file_name, file_mode)
		for tape_item in self.tape:
			if tape_item['type'] == 'Trade':
				dumpfile.write('Trd, %010.3f, %s\n' % (tape_item['time'], tape_item['price']))
		dumpfile.close()
		if tape_mode == 'wipe':
			self.tape = []

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
			'n': self.bids.number_orders,
			'lob': self.bids.lob_anon}
		public_data['asks'] = {
			'best': self.asks.best_price,
			'worst': self.asks.worstprice,
			'sess_hi': self.asks.session_extreme,
			'n': self.asks.number_orders,
			'lob': self.asks.lob_anon}
		public_data['quote_id'] = self.quote_id
		public_data['tape'] = self.tape
		if verbose:
			print('publish_lob: t=%d' % cur_time)
			print('BID_lob=%s' % public_data['bids']['lob'])
			print('ASK_lob=%s' % public_data['asks']['lob'])

		return public_data

	def __str__(self):
		return "exchange"
