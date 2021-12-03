#coding: UTF-8

import hashlib
import json
import requests

from time import time
from uuid import uuid4
from urllib.parse import urlparse

from flask import Flask, jsonify, request

class Blockchain(object):
	def __init__(self):
		self.chain = []
		self.current_transactions = []
		self.nodes = set()

		# make genesis block
		self.new_block(previous_hash=1, proof=100)
	
	def register_node(self, address):
		parsed_url = urlparse(address)
		self.nodes.add(parsed_url.netloc)
	
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
		while self.valid_proof(last_proof, proof) is False:
			proof += 1
		
		return proof
	
	@staticmethod
	def valid_proof(last_proof, proof):
		# check is proof is correct
		guess = f'{last_proof}{proof}'.encode()
		guess_hash = hashlib.sha256(guess).hexdigest()

		return guess_hash[:4] == "0000"
	
	def valid_chain(self, chain):
		last_block = chain[0]
		current_index = 1

		while current_index < len(chain):
			block = chain[current_index]
			print(f'{last_block}')
			print(f'{block}')
			print("\n--------------n")

			# chech if block's hash is correct
			if block['previous_hash'] != self.hash(last_block):
				return False
			
			# chech if PoW is correct
			if not self.valid_proof(last_block['proof'], block['proof']):
				return False
			
			last_block = block
			current_index += 1
		
		return True
	
	def resolve_conflicts(self):
		neighbors = self.nodes
		new_chain = None

		max_length = len(self.chain)

		for node in neighbors:
			response = requests.get(f'http://{node}/chain')

			if response.status_code == 200:
				length = response.json()['length']
				chain = response.jsonn()['chain']

				if length > max_length and self.valid_chain(chain):
					max_length = length
					new_chain = chain
		
		if new_chain:
			self.chain = new_chain
			return True
		
		return False


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
	last_block = blockchain.last_block
	last_proof = last_block['proof']
	proof = blockchain.proof_of_work(last_proof)

	blockchain.new_transaction(
		sender="0",
		recipient=node_identifier,
		amount=1,
	)

	block = blockchain.new_block(proof)

	response = {
		'message': 'mined new block',
		'index': block['index'],
		'transactions': block['transactions'],
		'proof': block['proof'],
		'previous_hash': block['previous_hash'],
	}
	return jsonify(response), 200

@app.route('/chain', methods=['GET'])
def full_chain():
	response = {
		'chain': blockchain.chain,
		'length': len(blockchain.chain),
	}
	return jsonify(response), 200

@app.route('/nodes/register', methods=['POST'])
def register_node():
	values = request.get_json()

	nodes = values.get('nodes')
	if nodes is None:
		return "Error: Invalid node list", 400
	
	for node in nodes:
		blockchain.register_node(node)
	
	response = {
		'message': 'new node was added',
		'total_nodes': list(blockchain.nodes),
	}
	return jsonify(response), 201

@app.route('/nodes/resolve', methods=['GET'])
def consensus():
	replaced = blockchain.resolve_conflicts()

	if replaced:
		response = {
			'message': 'chain was replaced',
			'new_chain': blockchain.chain
		}
	else:
		response = {
			'message': 'chain was not replaced',
			'chain': blockchain.chain
		}
	return jsonify(response), 200

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=5000)
