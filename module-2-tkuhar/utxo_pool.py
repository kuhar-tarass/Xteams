from block import Block
import transaction

class UTXOP:
    pool = {}

    def __init__(self):
        """ Load pool from files to RAM """
        pass
    
    def update_pool(self, block:Block):
        for tx in block:
            txid = tx.txid()
            for tx_in in tx.inputs:
                if tx_in.txid in self.pool and tx_in.txid.vout in self.pool[tx_in.txid]:
                    del self.pool[tx_in.txid][tx_in.txid.vout]
                    if len(self.pool[tx_in.txid]) == 0:
                        del self.pool[tx_in.txid]
                else:
                        # raise Exception("non valid input")
                        print(f"non valid input ")
            for tx_out in tx.outputs:
                i = 0
                if txid in self.pool:
                    self.pool[txid][i] = tx_out
                else:
                    self.pool[txid] = {i:tx_out}
                i += 1

    def find_out(self, txid:bytearray, vout: int):
        if txid in self.pool and vout in self.pool[txid]:
            return self.pool[txid][vout]
        else:
            return None
    
    
    def find_address(self, address):
        """ find and return list of all outputs for address"""
        res = []
        for tx in self.pool:
            for out in tx:
                if out.recipient_address == address:
                    res.append(out)
        return res
#%%
