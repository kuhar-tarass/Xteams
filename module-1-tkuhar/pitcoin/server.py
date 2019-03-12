import transaction, pending_pool
import os, time, flask
from flask import Flask, request, json
from blockchain import Blockchain
from threading import Thread

app = Flask(__name__)
bc = Blockchain() 
try:
    bc.import_chain()
except Exception as e:
    print (str(e))

@app.route('/mine/genesis', methods=['POST'])
def mining_genesis():
    if bc.mining == False:
        bc.mining = True
        thread = Thread(target = bc.genesis_block)
        thread.start()
    return "Done!"


@app.route('/mine', methods=['POST'])
def mining_controler():
    if len(bc.chain) == 0:
        return "Havn`t genesis block"
    if request.data == b'1':
        print("start mining")
        if bc.mining == False:    
            bc.mining = True
            thread = Thread(target = bc.mine)
            thread.start()
    else:
        print("stop mining")
        bc.mining = False
    return "Done"

@app.route('/transaction/new', methods=['POST'])
def add_new_transaction():
    try:
        tx  = request.data.decode()
        bc.submit_tx(tx)
    except:
        return ("Bad transaction")
    return("Transaction added")


@app.route('/transaction/pendings', methods=['POST'])
def pendings_tx():
    if os.path.exists(os.path.abspath(".") + "/mempool"):
        try:
            with open(os.path.abspath(".") + "/mempool", 'r') as file:
                txs = file.readlines()
            return json.dumps(txs)
        except Exception as s:
            return("Error: Can`t get transactions")


@app.route('/chain', methods=['POST'])
def get_full_chain():
    return json.dumps([block.__dict__() for block in bc.chain])


@app.route('/chain/length', methods=['POST'])
def chain_length():
    return len(bc.chain)


@app.route('/nodes', methods=['POST'])
def get_nodes():
    return json.dumps(bc.nodes)


@app.route('/nodes/add_node', methods=['POST'])
def add_node():
    try:
        bc.add_node(request.data)
    except Exception as e:
        return e
    else:
        return "Address added"

if __name__ == "__main__":
    app.run(debug=True)
