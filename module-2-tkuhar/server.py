import transaction
import pending_pool
import os
import time
import flask
from flask import Flask, request, json
from blockchain import Blockchain
from threading import Thread

app = Flask(__name__)
bc = Blockchain()
try:
    bc.import_chain()
    bc.import_node()
except Exception as e:
    print(str(e))


@app.route('/mine/genesis', methods=['POST'])
def mining_genesis():
    if bc.mining == False:
        bc.mining = True
        thread = Thread(target=bc.genesis_block)
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
            thread = Thread(target=bc.mine)
            thread.start()
    else:
        print("stop mining")
        bc.mining = False
    return "Done"


@app.route('/transaction/new', methods=['POST'])
def add_new_transaction():
    tx = request.data.decode()
    bc.submit_tx(tx)
    # try:
    # except Exception as e:
        # return (f"Bad transaction {e}")
    return("Transaction added")


@app.route('/transaction/pendings', methods=['POST'])
def pendings_tx():
    if os.path.exists(os.path.abspath(".") + "/mempool"):
        try:
            with open(os.path.abspath(".") + "/mempool", 'r') as file:
                txs = file.readlines()
            return json.dumps(txs)
        except Exception as s:
            return(f"Error: Can`t get transactions[{s}")


@app.route('/chain', methods=['POST'])
def get_full_chain():
    return json.dumps([block.__dict__ for block in bc.chain])


@app.route('/chain/length', methods=['POST'])
def chain_length():
    return str(len(bc.chain))


@app.route('/nodes', methods=['POST'])
def get_nodes():
    return json.dumps(bc.nodes)


@app.route('/nodes/add_node', methods=['POST'])
def add_node():
    try:
        bc.add_node(request.data.decode())
    except Exception as e:
        return e
    else:
        return "Address added"


@app.route('/getbalance', methods=['POST'])
def get_balance():
    balance = bc.get_ballance(request.data.decode())
    # print(request.data.decode(), len(bc.chain))
    return str(balance)

@app.route('/get_uout/', methods=['POST'])
def get_uout():
    address = request.data.decode()
    result = bc.get_uout(address)
    return result


@app.route('/ping', methods = ['POST'])
def ping():
    bc.ping()
    return "OK"


@app.route('/valide_chain', methods=['POST'])
def valide_chain():
    bc.is_valide_chain()
    try:
        pass
    except Exception as e:
        return f"Error {e}"
    else:
        return "OK"

@app.route('/resolve_conflicts', methods=['POST'])
def resolve_conflicts():
    try:
        bc.resolve_confilcts()
    except Exception as e:
        return f"Error {e}"
    else:
        return "OK"

if __name__ == "__main__":
    app.run(debug=True)
