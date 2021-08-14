class Order:
	"""
	@author Jiale Ma
	"""

	def __init__(self, trader_id="", order_type="", price=0, quantity=0, time="", quote_id=0):
		# trader i.d.
		self.trader_id = trader_id
		# order type
		self.order_type = order_type
		# price
		self.price = price
		# quantity
		self.quantity = quantity
		# timestamp
		self.time = time
		# quote i.d. (unique to each quote)
		self.quote_id = quote_id

	def __str__(self):
		return "[%s %s P=%.3f Q=%s T=%5.2f quote_id:%d]" % (
			self.trader_id, self.order_type, self.price, self.quantity, self.time, self.quote_id)
