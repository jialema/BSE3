import sys
import logging


def create_log():
	logger = logging.getLogger("logger")
	logger.setLevel(logging.DEBUG)

	file_handler = logging.FileHandler("bse.log")
	file_handler.setLevel(logging.DEBUG)

	formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
	file_handler.setFormatter(formatter)

	logger.addHandler(file_handler)
	return logger

def process_trades(trades, traders, order, cur_time):
	for trade in trades:
		if trade is not None:
			# trade occurred so the counterparties update order lists and blotters
			traders[trade["ask"]].book_keep(trade, order, cur_time)
			traders[trade["bid"]].book_keep(trade, order, cur_time)


def get_code_position():
	position = "File \"{}\", line {}, in {}".format(
		sys._getframe().f_code.co_filename,
		sys._getframe().f_lineno,
		sys._getframe().f_code.co_name)
	return position


logging.basicConfig(level=logging.DEBUG, format=' %(asctime)s - %(levelname)s -%(message)s')
logging.debug('Some debugging details.')
logging.info('The logging module is working')
logging.warning('An error message is about to be logged.')
logging.error('An error has occurred.')
logging.critical('The program is unable to recover!')