class Order:
	"""
	@author Jiale Ma
	"""

	def __init__(self, trader_id="", order_type="", price=0, quantity=0, time="", quote_id=""):
		self.trader_id = trader_id  # trader i.d.
		self.order_type = order_type  # order type
		self.price = price  # price
		self.quantity = quantity  # quantity
		self.time = time  # timestamp
		self.quote_id = quote_id  # quote i.d. (unique to each quote)

	def __str__(self):
		return "[%s %s P=%03d Q=%s T=%5.2f quote_id:%d]" % (
			self.trader_id, self.order_type, self.price, self.quantity, self.time, self.quote_id)
