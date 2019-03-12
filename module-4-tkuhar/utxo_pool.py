from block import Block
import transaction
from serializer import Serializer, Deserializer
from wallet import base58_decode

class UTXOP:
    pool = {}
    net = 0x6f

    def __init__(self):
        """ Load pool from files to RAM """
        pass
    
    def update_pool(self, block:Block):
        for tx in block.transactions:
            tx_obj = Deserializer.deserialize(tx)
            txid = tx_obj.txid().hex()
            for tx_in in tx_obj.inputs:
                if tx_in.txid.hex() == 64*'0':
                    pass  
                elif (tx_in.txid.hex() in self.pool) and (tx_in.vout in self.pool[tx_in.txid.hex()]):
                    del self.pool[tx_in.txid.hex()][tx_in.vout]
                    if len(self.pool[tx_in.txid.hex()]) == 0:
                        del self.pool[tx_in.txid.hex()]
                else:
                    pass
                    # raise Exception("non valid input")
            i = 0
            for tx_out in tx_obj.outputs:
                if txid in self.pool:
                    self.pool[txid][i] = tx_out
                else:
                    self.pool[txid] = {i:tx_out}
                i += 1

    def find_out(self, txid:bytearray, vout: int):
        txid = txid.hex()
        if txid in self.pool and vout in self.pool[txid]:
            return (txid, vout, self.pool[txid][vout])
        else:
            raise "[Tx input missed in utxo pool]"
    
    
    def find_address(self, address):
        """ find and return list of all outputs for address"""
        res = []
        for tx, outputs in self.pool.items():
            for vout, out in outputs.items():
                if out.recipient_address == address:
                    res.append((tx, vout ,out))
        return res
#%%


# i = 0
# pool = {}
# a = [i for i in range(0, 15) ]
# txid = 1
# for tx_out in a:
#     if txid in pool:
#         pool[txid][i] = tx_out
#     else:
#         pool[txid] = {i:tx_out}
#     # pool[txid] = {i:tx_out}
#     i += 1



# print(pool)

#%%
