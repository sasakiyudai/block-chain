#coding: UTF-8

class Blockchain(object):
	def __init__(self):
		self.chain = []
		self.current_transactions = []
	
	def new_block(self):
		# add new block into chain
		pass
	
	def new_transaction(self):
		# add new transaction into transactions
		pass

	@staticmethod
	def hash(block):
		# hash block
		pass

	@property
	def last_block(self):
		# return last block
		pass