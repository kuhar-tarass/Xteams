#%%:
from merkle import merkle_root
from tx_valiadtor import check_tx
from hashlib import sha256
from time import time
import json


class Block:
    def __init__(self, timestamp, previous_hash, transactions, nonce = 0):
        self.height = 0
        # self.bits = bits
        self.timestamp = timestamp
        self.nonce = nonce
        self.previous_hash = previous_hash
        self.transactions = transactions
        self.merkle_root = merkle_root(transactions)


    def get_hash(self) ->bytearray:                                             # ! not ended 
        sum = sha256(
                (
                str(self.timestamp)
                + str(self.nonce)
                + self.previous_hash
                + self.merkle_root
                ).encode()
            ).digest()
        return sum


    def validate_txs(self):                                                     # ! not ended
        try:
            for i in self.transactions:
                check_tx(i)
        except Exception as what:
            print (what)

    @staticmethod
    def from_json( j_block:dict):
        height = int(j_block['height'])
        # bits = int(j_block['bits'])
        timestamp = int(j_block['timestamp'])
        nonce = int(j_block['nonce'])
        previous_hash = j_block['previous_hash']
        transactions = j_block['transactions']
        merkle_root = j_block["merkle_root"]
        block = Block(timestamp, previous_hash, transactions, nonce=nonce)
        block.height = height
        if block.merkle_root != merkle_root:
            raise Exception("Brocken blocks[m_root]")
        return block