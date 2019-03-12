import transaction
import pending_pool
import os
import time
import flask
import pprint
from flask import Flask, request, json
from blockchain import Blockchain
from threading import Thread

app = Flask(__name__)
_program_dir = os.path.dirname(os.path.abspath(__file__))
bc = Blockchain()



@app.route('/mine/genesis', methods=['POST'])
def s_mining_genesis():
    if bc.mining == False:
        thread = Thread(target=bc.genesis_block)
        thread.start()
    return "Done!"


@app.route('/mine', methods=['POST'])
def s_mining_controler():
    if len(bc.chain) == 0:
        return "Havn`t genesis block", 400
    if request.data == b'1':
        print("start mining")
        if bc.mining == False:
            bc.mining = True
            thread = Thread(target=bc.mine)
            thread.start()
            return "Mining start", 200
    else:
        print("stop mining")
        bc.mining = False
        return "Mining stop", 200
    return "Done"


@app.route('/transaction/new', methods=['POST'])
def s_add_new_transaction():
    try:
        tx = request.data.decode()
        bc.submit_tx(tx)
    except Exception as e:
        return (f"Bad transaction {e}")
    return("Transaction added")


@app.route('/transaction/pendings', methods=['POST'])
def s_pendings_tx():
    if os.path.exists(_program_dir + "/mempool"):
        try:
            with open(_program_dir + "/mempool", 'r') as file:
                txs = file.readlines()
            return json.dumps(txs)
        except Exception as s:
            return(f"Error: Can`t get transactions[{s}")


@app.route('/chain', methods=['POST', 'GET'])
def s_get_full_chain():
    if flask.request.method == 'POST':
        return json.dumps([block.__dict__ for block in bc.chain])
    elif request.method =='GET':
        return  json.dumps([block.__dict__ for block in bc.chain], indent= 4)


@app.route('/chain/length', methods=['POST'])
def s_chain_length():
    return str(len(bc.chain))


@app.route('/nodes', methods=['POST'])
def s_get_nodes():
    return json.dumps(bc.nodes)


@app.route('/nodes/add_node', methods=['POST'])
def s_add_node():
    try:
        bc.add_node(request.data.decode())
    except Exception as e:
        return e
    else:
        return "Address added", 200

@app.route('/ping', methods = ['POST'])
def s_ping():
    try:
        a = bc.ping()
        return f"{a}"
    except Exception as e:
        print(e)
    return "Error", 400


@app.route('/chain/valide_chain', methods=['POST'])
def s_valide_chain():
    bc.is_valide_chain()
    try:
        pass
    except Exception as e:
        return f"Error {e}" , 400
    else:
        return "OK"

@app.route('/resolve_conflicts', methods=['POST'])
def s_resolve_conflicts():
    try:
        bc.resolve_confilcts()
    except Exception as e:
        return f"Error {e}"
    else:
        return "OK"


@app.route('/utxo/getbalance', methods=['POST'])
def s_get_balance():
    balance = bc.get_ballance(request.data.decode())
    return str(balance)


@app.route('/utxo/get_uout', methods=['POST'])
def s_get_uout():
    address = request.data.decode()
    result = bc.get_uout(address)
    return result


@app.route('/utxo', methods =['GET', 'POST'])
def s_utxo():
    try:
        a = bc.utxop.pool
        if flask.request.method == 'POST':
            return f"{a}",200
        elif request.method =='GET':
            # perty_a = [(i, vout, out.value) for i , vout, out in a]
            return pprint.pformat(a,indent=4, width=100),200
    except Exception as e:
        return f'Error: {e}',400


@app.route('/get_difficluty', methods =['GET', 'POST'])
def s_get_difficult():
    try:
        dif = bc.get_difficluty()
        # print (dif)
        return str(dif), 200
    except Exception as e:
        pass
    return "", 400

if __name__ == "__main__":    
    app.run(debug=True, port=5000)

