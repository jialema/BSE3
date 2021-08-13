from order_book_half import OrderBookHalf

# minimum price in the system, in cents/pennies
BSE_SYS_MIN_PRICE = 1
# maximum price in the system, in cents/pennies
BSE_SYS_MAX_PRICE = 1000


class OrderBook:

	def __init__(self):
		self.bids = OrderBookHalf('Bid', BSE_SYS_MIN_PRICE)
		self.asks = OrderBookHalf('Ask', BSE_SYS_MAX_PRICE)
		self.tape = []
		# unique ID code for each quote accepted onto the book. count from 0
		self.quote_id = 0

	def __str__(self):
		return "OrderBook"


