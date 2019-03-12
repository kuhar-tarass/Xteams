#%%:
from merkle import merkle_root
from tx_valiadtor import check_tx
from hashlib import sha256
from time import time
#%%:
class Block:
    def __init__(self, timestamp, previous_hash, transactions, nonce = 0):
        self.height = 0
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



#%%:
# import json
# from hashlib import sha256
# # a = sha256(b"1234").__dict__
# a = ['a','a','a','a']
# print ("".join(a))
# print( json.dumps( a ) ) 
# 

#%%
