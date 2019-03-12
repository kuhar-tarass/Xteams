# import hashlib
from hashlib import sha256

#%%:
class Transaction:
    def __init__(self, recipient:str = 0, amount = 0):
        self.sender = ""                 #! check address
        self.recipient = recipient      #! check address
        self.amount = amount
        self.sender_pubkey = 0
        self.sign = 0

    def hash(self) -> bytearray:
        return sha256(
                (
                self.sender 
                + self.recipient 
                + str(self.amount)
                ).encode()
            ).digest()




class CoinbaseTransaction(Transaction):
    def __init__(self, recipient:str = 0):
        self.sender = 34*'0'              # ? some set of zeros (?!?!)
        self.recipient = ""
        self.amount = 50
        self.signature = 0              # ? sign transaction with miner`s key (get this key from ```minerkey``` file (WIF format ))
