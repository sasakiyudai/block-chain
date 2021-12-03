#coding: UTF-8

import hashlib
import json

from time import time
from uuid import uuid4

from flask import Flask, jsonify, request

class Blockchain(object):
	def __init__(self):
		self.chain = []
		self.current_transactions = []

		# make genesis block
		self.new_block(previous_hash=1, proof=100)
	
	def new_block(self, proof, previous_hash=None):
		# add new block into chain
		block = {
			'index': len(self.chain) + 1,
			'timestamp': time(),
			'transactions': self.current_transactions,
			'proof': proof,
			'previous_hash': previous_hash or self.hash(self.chain[-1]),
		}

		# reset current_transactions
		self.current_transactions = []

		self.chain.append(block)
		return block
	
	def new_transaction(self, sender, recipient, amount):
		# add new transaction into list
		self.current_transactions.append({
			'sender': sender,
			'recipient': recipient,
			'amount': amount,
		})

		# return the index into which above current_transactions will be added
		return self.last_block['index'] + 1

	@staticmethod
	def hash(block):
		# hash block (SHA-256)
		block_string = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()

	@property
	def last_block(self):
		# return last block
		return self.chain[-1]

	def proof_of_work(self, last_proof):
		# simple PoW
		proof = 0
		while self.valid_prrof(last_proof, proof) is False:
			proof += 1
		
		return proof
	
	@staticmethod
	def valid_proof(last_proof, proof):
		# check is proof is correct
		guess = f'{last_proof}{proof}'
		guess_hash = hashlib.sha256(guess).hexdigest()

		return guess_hash[:4] == "0000"


app = Flask(__name__)
node_identifier = str(uuid4()).replace('-', '')

blockchain = Blockchain()

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
	values = request.get_json()

	required = ['sender', 'recipient', 'amount']
	if not all(k in values for k in required):
		return 'Missing values', 400
	
	index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

	response = {'message': f'transaction was added into block {index}'}
	return jsonify(response), 201


@app.route('/mine', methods=['GET'])
def mine():
	return 'mine new block'

@app.route('/chain', methods=['GET'])
def full_chain():
	response = {
		'chain': blockchain.chain,
		'length': len(blockchain.chain),
	}
	return jsonify(response), 200

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
