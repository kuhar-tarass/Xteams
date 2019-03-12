# %%:
import pending_pool
import wallet
from tx_valiadtor import check_tx
from transaction import CoinbaseTransaction
from serializer import Serializer, Deserializer
from block import Block
from time import time_ns
import os
import json
import requests
from utxo_pool import UTXOP

# %%:
_program_dir = os.path.dirname(os.path.abspath(__file__))


class Blockchain:
    n_zero_hardnes = 6
    mining_difficulty = 0
    mining_max_target_bits = 0x1903a30c
    mining_max_target = 0x0000ffff00000000000000000000000000000000000000000000000000000000
    mining_target =     0x00000ffff0000000000000000000000000000000000000000000000000000000
    mining_time = 60000000000
    mining = False
    chain = []
    nodes = set()
    miner_key = None
    utxop = None
    net = 0x6f

    def __init__(self):
        try:
            self.import_chain()
            self.import_node()
            self.init_utxop()
        except Exception as e:
            print(f'_init_{e}')

    def get_mining_time_last_blocks(self):
        if len(self.chain) > 3:
            return time_ns() - self.chain[-3].timestamp
        else:
            return (time_ns() - self.chain[-1].timestamp) * 3
        

    def get_difficluty(self):
        return self.mining_max_target / self.mining_target

    
    def change_difficult(self):
        mine_time = self.get_mining_time_last_blocks()
        coef =  mine_time / self.mining_time
        # print(f'{mine_time}__{self.mining_time}__{coef}')
        if not (0.85 < coef < 1.15):
            coef = 0.85 if coef < 1 else 1.15
        self.mining_target = self.mining_target * coef
        # if self.mining_target > self.mining_max_target:
        #     self.mining_target = self.mining_max_target
        
    

    def get_miner_key(self):
        try:
            self.miner_key = wallet.f_import_private(_program_dir + "/minerkey", net=self.net)
        except Exception as e:
            print (f"Import miner key error [{e}]")


    def mine(self):
        if len(self.chain) == 0:
            print("Havn`t genesis block")
            self.mining = False
            return
        if self.miner_key == None:
            self.get_miner_key()
        while (self.mining):
            self.resolve_confilcts()
            if (self.chain[-1].height + 1) % 5 == 0:
                self.change_difficult()
            new_block = self.mine_block()
            if new_block:
                self.add_block(new_block)
            # self.mining = False


    def add_block(self, new_block):
        self.chain.append(new_block)
        self.utxop.update_pool(new_block)
        if not os.path.exists(_program_dir + "/chain/"):
            os.makedirs(_program_dir + "/chain")
        with open(_program_dir + "/chain" + "/block_" + str(new_block.timestamp), "w") as f:
            f.write(json.dumps(new_block.__dict__))


    def mine_block(self):
        txs = pending_pool.get_last_tx()
        for tx in txs:
            try:
                dec_tx = Deserializer.deserialize(tx)
                prev_outputs = []
                for i in dec_tx.inputs:
                    txid, vout, out = self.utxop.find_out(txid=i.txid, vout=i.vout)
                    prev_outputs.append((txid, vout, out))
                if not check_tx(dec_tx, prev_outputs):
                    print("Non_valid input")
                    raise Exception("Non valid input")
            except Exception as e:
                txs.remove(tx)
                print(f'Error: invalid tx {dec_tx.txid()[::-1].hex()}[{e}]')

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
        # start_time = time_ns()
        while self.mining:
            if int (block.get_hash().hex(), 16) < self.mining_target:
                return block
            else:
                block.nonce += 1
        return 0


    def ping(self):
        a = ""
        for node in self.nodes:
            try:
                rq = requests.post(node + "/ping").text
            except :
                rq = f'Unavalible'
            a += f'Status [{node}]: {rq}\n'
        return a


    def resolve_confilcts(self):
        my_height = len(self.chain)
        other_heigths = {}
        for node in self.nodes:
            try:
                other_heigths[node] = int(requests.post(node + "/chain/length").text)
            except Exception:
                pass
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
                    self.init_utxop()
                for new_block in new_chain:
                    self.add_block(new_block) 


    def delete_chain(self):
        chain_dir = _program_dir + '/chain'

        for i in range(len(self.chain)):
            os.remove(f'{chain_dir}/block_{self.chain[i].timestamp}')
            del self.chain[i]
        self.utxop = 0
                    

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
        with open(_program_dir + "/nodes", 'w') as f:
            f.writelines([i + '\n' for i in self.nodes])


    def coinbase_tx(self, value):
        coin_tx = CoinbaseTransaction(recipient=self.miner_key.get_address(), value=value)
        return Serializer.serialize(coin_tx)


    def genesis_block(self):
        if self.miner_key == None:
            self.get_miner_key()
        if len(self.chain) > 0:
            return
        timestamp = time_ns()
        coin_tx = self.coinbase_tx(25)
        genesis = Block(
            timestamp=timestamp,
            previous_hash=64*'0',
            transactions=[coin_tx]
        )
        self.mining = True        
        self.find_nonce(genesis)
        self.mining = False
        self.add_block(genesis)


    def submit_tx(self, tx):
        pending_pool.add_tx(tx)
        return("Transaction added")

    
    def import_node(self):
        if not os.path.exists(_program_dir + "/nodes"):
            return
        with open(os.path.join(_program_dir + "/nodes"), 'r') as file:
            result = file.readlines()
        for a in result:
            self.nodes.add(a.rstrip())
        

    def import_chain(self):
        chain_dir = _program_dir + '/chain'
        if os.path.isdir(chain_dir):
            onlyfiles = [f for f in os.listdir(chain_dir) if os.path.isfile(f'{chain_dir}/{f}')]
            onlyfiles.sort()
            for f in onlyfiles:
                with open(os.path.join(chain_dir, f), "r") as file:
                    ss = file.read()
                    bb = Block.from_json(json.loads(ss))
                    if len(self.chain) != 0:
                        if self.chain[-1].get_hash().hex() != bb.previous_hash:
                            raise Exception(f"Broken blocks (filename[{f}])[{self.chain[-1].get_hash().hex()}]")
                    self.chain.append(bb)


    def get_ballance(self, address: str):
        balance = 0
        outputs = self.utxop.find_address(address)
        for o in outputs:
            balance += o[-1].value
        return balance


    def get_uout(self,address):
        res = self.utxop.find_address(address)
        res = [(txid, vout, Serializer.serialize_output(o)) for txid, vout, o in res]
        return json.dumps(res)


    def init_utxop(self, file = 0):
        if not file:
            self.utxop  = UTXOP()
            for block in self.chain:
                self.utxop.update_pool(block)
        else:
            pass 

        

# %%
