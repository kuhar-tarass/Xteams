# %%:
# import sys
# sys.path.append("/Users/tkuhar/X.Teams/module_1/pitcoin")
import cmd
import sys
import os.path
import requests
import wallet
from wallet import k_box
import tx_valiadtor
from transaction import Transaction
from serializer import Serializer, Deserializer


# %%:
class miner_cli(cmd.Cmd):
    intro = 'Welcome to the miner-cli shell.   Type help or ? to list commands.\n'
    prompt = '(miner-cli)$ '
    key_pair = 0
    node_address = "http://127.0.0.1:5000"


    def do_exit(self, inp):
        return True
    do_EOF = do_exit


    def do_add_node(self, args):
        try:
            rq = requests.post(self.node_address + "/nodes/add_node", args)
            print(rq.text)
        except Exception:
            print("Server unavalible")
        return False

    def do_start_mine(self, args):
        'Start mining'
        try:
            rq = requests.post(self.node_address + "/mine", data=b'1')
            print(rq.text)
        except Exception:
            print("Server unavalible")
        return False

    def do_stop_mine(self, args):
        'Stop mining'
        try:
            rq = requests.post(self.node_address + "/mine", data=b'0')
            if rq.status_code == 200:
                print("Mining stopped")
            else:
                print (rq.text)
        except Exception:
            print("Server unavalible")
        return False

    def do_genesis_block(self, args):
        'Make genesis block'
        try:
            rq = requests.post(self.node_address + "/mine/genesis", data="")
            print(rq.text)
        except Exception:
            print("Server unavalible")
        return False

    def do_ping(self,args):
        try:
            rq = requests.post(self.node_address + '/ping', data="")
            print(rq.text)
        except:
            pass
        return False

    def do_resolve_conflicts(self, args):
        try:
            rq = requests.post(self.node_address + '/resolve_conflicts')
            print (rq.text)
        except:
            pass
        return False

    def do_check_chain(self, args):
        try:
            rq = requests.post(self.node_address + '/chain/valide_chain')
            print (rq.text)
        except:
            print("Server unavalible")

    def do_connect_node(self, args):
        'connect to blockchain server'
        args = args.split()
        if len(args) != 1:
            print ("Error")
            return False
        self.node_address = args[0]
        try:
            print("local node: OK")
            rq = requests.post(self.node_address + '/ping', data="")
        except:
            print("Server unavalible")

# ? get public key(WIF) from file  named ```privkey```
# ? save address to file named ```address```


# %%:
def main():
    miner_cli().cmdloop()
    print("Stoped")


if __name__ == "__main__":
    main()