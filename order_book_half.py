

class OrderBookHalf:
	"""
	@author Jiale Ma
	"""

	def __init__(self, book_type, worst_price):
		# book type: bids or asks?
		self.book_type = book_type
		# dictionary of orders received, indexed by Trader ID
		self.orders = {}
		# limit order book, dictionary indexed by price, with order info
		self.lob = {}
		# anonymized LOB, lists, with only price/quantity info
		self.lob_anon = []
		# summary stats
		self.best_price = None
		self.best_trader_id = None
		self.worst_price = worst_price
		self.session_extreme = None  # most extreme price quoted in this session
		self.number_orders = 0  # how many orders?
		self.lob_depth = 0  # how many different prices on lob?

	def anonymize_lob(self):
		"""
		anonymize a lob, strip out order details, format as a sorted list
		NB for asks, the sorting should be reversed
		"""
		self.lob_anon = []
		for price in sorted(self.lob):
			quantity = self.lob[price][0]
			self.lob_anon.append([price, quantity])

	def build_lob(self):
		"""
		take a list of orders and build a limit-order-book (lob) from it
		NB the exchange needs to know arrival times and trader-id associated with each order
		returns lob as a dictionary (i.e., unsorted)
		also builds anonymized version (just price/quantity, sorted, as a list) for publishing to traders
		"""
		self.lob = {}
		for trader_id in self.orders:
			order = self.orders.get(trader_id)
			price = order.price
			if price in self.lob:
				# update existing entry
				quantity = self.lob[price][0]
				order_list = self.lob[price][1]
				order_list.append([order.time, order.quantity, order.trader_id, order.quote_id])
				self.lob[price] = [quantity + order.quantity, order_list]
			else:
				# create a new dictionary entry
				self.lob[price] = [order.quantity, [[order.time, order.quantity, order.trader_id, order.quote_id]]]
		# create anonymized version
		self.anonymize_lob()
		# record best price and associated trader-id
		if len(self.lob) > 0:
			if self.book_type == 'Bid':
				self.best_price = self.lob_anon[-1][0]
			else:
				self.best_price = self.lob_anon[0][0]
			self.best_trader_id = self.lob[self.best_price][1][0][2]
		else:
			self.best_price = None
			self.best_trader_id = None

	def book_add(self, order):
		"""
		add order to the dictionary holding the list of orders
		either overwrites old order from this trader
		or dynamically creates new entry in the dictionary
		so, max of one order per trader per list
		checks whether length or order list has changed, to distinguish addition/overwrite
		"""
		# if this is an ask, does the price set a new extreme-high record?
		if (self.book_type == 'Ask') and ((self.session_extreme is None) or (order.price > self.session_extreme)):
			self.session_extreme = int(order.price)

		number_orders = self.number_orders
		self.orders[order.trader_id] = order
		self.number_orders = len(self.orders)
		self.build_lob()
		if number_orders != self.number_orders:
			return 'Addition'
		else:
			return 'Overwrite'

	def book_del(self, trader_id):
		"""
		delete order from the dictionary holding the orders
		assumes max of one order per trader per list
		checks that the Trader ID does actually exist in the dict before deletion
		"""
		if self.orders.get(trader_id) is not None:
			del (self.orders[trader_id])
			self.number_orders = len(self.orders)
			self.build_lob()

	def delete_best(self):
		"""
		delete order: when the best bid/ask has been hit, delete it from the book
		the Trader ID of the deleted order is return-value, as counterparty to the trade
		"""
		best_price_orders = self.lob[self.best_price]
		# time priority principle
		best_price_quantity = best_price_orders[0]
		best_price_counterparty = best_price_orders[1][0][2]
		if best_price_quantity == 1:
			# here the order deletes the best price
			del (self.lob[self.best_price])
			del (self.orders[best_price_counterparty])
			self.number_orders = self.number_orders - 1
			if self.number_orders > 0:
				if self.book_type == 'Bid':
					self.best_price = max(self.lob.keys())
				else:
					self.best_price = min(self.lob.keys())
				self.lob_depth = len(self.lob.keys())
			else:
				self.best_price = self.worst_price
				self.lob_depth = 0
		else:
			"""
			best_bid_quantity > 1 so the order decrements the quantity of the best bid
			update the lob with the decremented order data
			"""
			self.lob[self.best_price] = [best_price_quantity - 1, best_price_orders[1][1:]]
			# update the bid list: counterpart's bid has been deleted
			del (self.orders[best_price_counterparty])
			self.number_orders = self.number_orders - 1
		self.build_lob()
		return best_price_counterparty
