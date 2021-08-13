def process_trades(trades, traders, order, cur_time):
	for trade in trades:
		if trade is not None:
			# trade occurred so the counterparties update order lists and blotters
			traders[trade["party1"]].book_keep(trade, order, cur_time)
			traders[trade["party2"]].book_keep(trade, order, cur_time)
