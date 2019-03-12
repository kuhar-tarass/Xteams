# %%:
import pending_pool
import wallet
from transaction import CoinbaseTransaction
from serializer import Serializer, Deserializer
from block import Block
from time import time_ns
import os
import json
import requests
from utxo_pool import UTXOP

# %%:


class Blockchain:
    n_zero_hardnes = 5
    mining_time = 300000000000
    mining = False
    chain = []
    nodes = set()
    miner_key = None
    utxop = None

    def get_miner_key(self):
        self.miner_key = wallet.f_import_private(os.path.abspath(".") + "/minerkey")


    def mine(self):
        if len(self.chain) == 0:
            print("Havn`t genesis block")
            self.mining = False
            return
        if self.miner_key == None:
            self.get_miner_key()
        while (self.mining):
            self.resolve_confilcts()
            new_block = self.mine_block()
            if new_block:
                self.add_block(new_block)
            self.mining = False


    def add_block(self, new_block):
        self.chain.append(new_block)
        if not os.path.exists(os.path.abspath(".") + "/chain/"):
            os.makedirs(os.path.abspath(".") + "/chain")
        with open(os.path.abspath("./chain") + "/block_" + str(new_block.timestamp), "w") as f:
            f.write(json.dumps(new_block.__dict__))


    def mine_block(self):
        txs = pending_pool.get_last_tx()
        fee = 25
        txs.insert(0, self.coinbase_tx(fee))
        timestamp = time_ns()
        previus_block_hash = self.chain[-1].get_hash().hex()
        new_block = Block(
            timestamp=timestamp,
            previous_hash=previus_block_hash,
            transactions=txs)
        new_block.height = self.chain[-1].height + 1
        new_block = self.find_nonce(new_block)
        return new_block


    def find_nonce(self, block):
        start_time = time_ns()
        while self.mining and ((time_ns() - start_time) < self.mining_time):
            if block.get_hash().hex()[0:self.n_zero_hardnes] == self.n_zero_hardnes*'0':
                return block
            else:
                block.nonce += 1
        return 0


    def ping(self):
        a = [requests.post(node + "/ping").text for node in self.nodes]
        print (f"_____a = {a}")


    def resolve_confilcts(self):
        my_height = len(self.chain)
        other_heigths = {node: int(requests.post(node + "/chain/length").text) for node in self.nodes}
        # print(f"other heigth {other_heigths} ")
        if not other_heigths:
            return
        max_heigth = max(other_heigths, key=other_heigths.get)
        if max_heigth in other_heigths:
            if other_heigths[max_heigth] > my_height:
                rq = requests.post(max_heigth + "/chain")
                tmp = json.loads(rq.text)
                new_chain = [Block.from_json(block) for block in tmp]
                if len(self.chain) != 0:
                    self.delete_chain
                for new_block in new_chain:
                    self.add_block(new_block) 


    def delete_chain(self):
        for i in range(len(self.chain)):
            os.remove('./chain/block_' + self.chain[i].timestamp)
            del self.chain[i]
                    

    def is_valide_chain(self):
        if len(self.chain) == 0:
            return
        prev = self.chain[0]
        prev.validate_txs()
        for i in range(1,len(self.chain)):
            if self.chain[i].previous_hash != prev.get_hash().hex():
                raise Exception(f"Invalide Block[{self.chain[i].timestamp}]")
            prev = self.chain[i]


    def add_node(self, address):
        self.nodes.add(address)
        with open(os.path.abspath(".") + "/nodes", 'w+') as f:
            f.writelines(self.nodes)


    def coinbase_tx(self, value):
        coin_tx = CoinbaseTransaction(recipient=self.miner_key.get_address(), value=value)
        return Serializer.serialize(coin_tx)


    def genesis_block(self):
        if self.miner_key == None:
            self.get_miner_key()
        timestamp = time_ns()
        coin_tx = self.coinbase_tx(25)
        genesis = Block(
            timestamp=timestamp,
            previous_hash=64*'0',
            transactions=[coin_tx]
        )
        self.find_nonce(genesis)
        self.mining = False
        self.add_block(genesis)


    def submit_tx(self, tx):
        pending_pool.add_tx(tx)
        return("Transaction added")

    
    def import_node(self):
        with open(os.path.join("./" + "nodes"), 'r') as file:
            result = file.readlines()
        for a in result:
            self.nodes.add(a.rstrip())
        

    def import_chain(self):
        if os.path.isdir(os.path.abspath("./chain")):
            onlyfiles = [f for f in os.listdir( './chain') if os.path.isfile(os.path.join('./chain', f))]
            onlyfiles.sort()
            for f in onlyfiles:
                with open(os.path.join('./chain', f), "r") as file:
                    ss = file.read()
                    bb = Block.from_json(json.loads(ss))
                    if len(self.chain) != 0:
                        if self.chain[-1].get_hash().hex() != bb.previous_hash:
                            raise Exception(f"Broken blocks[{self.chain[-1].get_hash().hex()}]")
                    self.chain.append(bb)


    def get_ballance(self, address: str):
        balance = 0
        outputs = self.utxop.find_address(address)
        for o in outputs:
            balance += o.value
        return balance


    def get_uout(self,address):
        res = self.get_ballance(address)
        res = [Serializer.serialize_output(i) for i in res]
        return json.dumps(res)


    def init_utxop(self, file = 0):
        if not file:
            self.utxop  = UTXOP()
            for block in self.chain:
                self.utxop.update_pool(block)
        else:
            pass 

        

# %%
