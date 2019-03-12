#%%:
import pending_pool, wallet
from transaction import CoinbaseTransaction
from serializer import Serializer
from block import Block
from time import time_ns
import os, json, requests

#%%:
class Blockchain:
    n_zero_hardnes = 5
    mining_time = 300000000000
    mining = False
    chain = []
    nodes = set()
    miner_key = None


    def get_miner_key(self):
        self.miner_key = wallet.f_import_private(os.path.abspath(".") + "/minerkey")


    def mine(self):
        if len(self.chain) == 0:
            print ("Havn`t genesis block")
            self.mining = False
            return
        if self.miner_key == None: self.get_miner_key()
        # self.mining = True
        # if True:
        while (self.mining):
            self.resolve_confilcts()
            new_block = self.mine_block()
            if new_block:
                self.add_block(new_block)
            # self.mining = False


    def add_block(self, new_block):
        self.chain.append(new_block)
        if not os.path.exists(os.path.abspath(".") + "/chain/"):
            os.makedirs(os.path.abspath(".") + "/chain")
        print (json.dumps(new_block.__dict__))
        with open(os.path.abspath("./chain") + "/block_" + str(new_block.timestamp), "w+") as f:
            f.write(json.dumps(new_block.__dict__))        
        

    def mine_block(self):
        txs = pending_pool.get_last_tx()
        txs.append(self.coinbase_tx())
        timestamp = time_ns()
        previus_block_hash = self.chain[-1].get_hash().hex()
        new_block = Block(
            timestamp=timestamp, 
            previous_hash=previus_block_hash,
            transactions=txs)
        new_block.height = self.chain[-1].height + 1    
        new_block =  self.find_nonce(new_block)
        return new_block


    def find_nonce(self, block):
        start_time = time_ns()
        while self.mining and ((time_ns() - start_time) < self.mining_time):
            if block.get_hash().hex()[0:self.n_zero_hardnes] == self.n_zero_hardnes*'0':
                return block
            else:
                block.nonce += 1
        else:
            return 0


    def resolve_confilcts(self):
        my_height = len(self.chain)
        other_heigths = {node: int(requests.post(node + "/chain/length").text)  for node in self.nodes}
        if other_heigths:
            max_heigth = max(other_heigths,key = other_heigths.get)
            if max_heigth in other_heigths:
                if other_heigths(max_heigth) > my_height:
                    pass                                                            # ! update our chain 

             
    def is_valide_chain(self):
        pass


    def add_node(self, address):
        self.nodes.add(address)
        with open(os.path.abspath(".") + "/nodes", 'w+') as f:
            f.writelines(self.nodes)

    
    def coinbase_tx(self):
        coin_tx = CoinbaseTransaction(recipient=self.miner_key.get_address())
        coin_tx.sender_pubkey = self.miner_key.get_public_key()
        coin_tx.sign = self.miner_key.sign(coin_tx.hash())
        return Serializer.serialize(coin_tx)


    def genesis_block(self):  
        if self.miner_key == None: self.get_miner_key()
        timestamp = time_ns()
        coin_tx = self.coinbase_tx()
        genesis = Block(
            timestamp=timestamp, 
            previous_hash=64*'0',
            transactions= [coin_tx]
            )
    
        self.find_nonce(genesis)
        self.mining = False
        self.add_block(genesis)


    def submit_tx(self, tx):
        pending_pool.add_tx(tx)
        return("Transaction added")


    def import_chain(self):
        if os.path.isdir(os.path.abspath("./chain")):
            onlyfiles = [f for f in os.listdir('./chain') if os.path.isfile(os.path.join('./chain', f))]
            for f in onlyfiles:
                with open(os.path.join('./chain', f), "r") as file:
                    ss = file.read()
                    bb = self.from_json(ss)
                    self.chain.append(bb)


    def from_json(self, sss):
        a = json.loads(sss)
        height = int(a['height'])
        timestamp = int(a['timestamp'])
        nonce = int(a['nonce'])
        previous_hash = a['previous_hash']
        transactions = a['transactions']
        merkle_root = a["merkle_root"]
        block = Block( timestamp, previous_hash, transactions,nonce=nonce)
        block.height = height
        if block.merkle_root != merkle_root:raise Exception ( "Brocken blocks")
        if len(self.chain) != 0:
            if self.chain[-1].get_hash().hex() != previous_hash: raise Exception ("Brocken blocks")
        return(block)



#%%