#coding: UTF-8

class Blockchain(object):
	def __init__(self):
		self.chain = []
		self.current_transactions = []
	
	def new_block(self):
		# add new block into chain
		pass
	
	def new_transaction(self, sender, recipient, amount):
		# add new transaction into list
		
		self.current_transactions.append({
			'sender': sender,
			'recipient': recipient,
			'amount': amount,
		})

		return self.last_block['index'] + 1

	@staticmethod
	def hash(block):
		# hash block
		pass

	@property
	def last_block(self):
		# return last block
		pass