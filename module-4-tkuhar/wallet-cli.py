# %%:
# import sys
# sys.path.append("/Users/tkuhar/X.Teams/module_1/pitcoin")
import cmd, sys, os.path, requests
import secrets
import wallet
import json
from wallet import k_box
import tx_valiadtor
from transaction import Transaction, Input, Output
from serializer import Serializer , Deserializer
import bip39, bip32


_program_dir = os.path.dirname(os.path.abspath(__file__))
FEE = 5000

# %%:
class wallet_cli(cmd.Cmd):
    intro = 'Welcome to the wallet-cli shell.   Type help or ? to list commands.\n'
    prompt = '(wallet)$'
    server_ip = "http://127.0.0.1:5000"
    key_pair = 0
    hd_key = 0
    net = 0x6f
    transactions = []
    unspend_pool = []

    def do_exit(self, inp):
        return True
    do_EOF = do_exit

    def do_dump_keys(self, inp):
        '-e --- extended format'
        inp = inp.split(' ')
        if len(inp) == 1 and inp[0] == "":
            if self.key_pair == 0:
                print("Error haven`t key pair")
                return False
            print(f"Private key(WIF): {wallet.to_WIF(self.key_pair.get_secret_key().hex())}")
            print(f"Address         : {self.key_pair.get_address()}")
        elif len(inp) == 1 and inp[0] == "-e":
            if self.hd_key == 0:
                print("Error haven`t hd_key")
                return False
            print(f"""extended_format:
                    {self.hd_key.Ext_format(privat = True)}
                    {self.hd_key.Ext_format(privat = False)} """)
        else:
            self.do_help("")
            return False

    def do_import_hd_key(self, inp):
        try:
            self.hd_key = bip32.bip32_key.from_xpub(inp)
            priv_key = self.hd_key.Prv_key()[1:]
            self.key_pair = k_box(priv_key.hex())
            with open(_program_dir + "/address", 'a') as f:
                f.write(f"{self.key_pair.get_address()}\n")
            print(f"Private key(WIF): {wallet.to_WIF(self.key_pair.get_secret_key().hex())}")
            print(f"Address         : {self.key_pair.get_address()}")
        except Exception as e:
            print(f'Error [{e}]')  
            return False


    def do_chain(self, inp):
        if self.hd_key == 0:
            print(" Haven`t hd key")
            return False
        try:
            tmp = bip32.chain(inp, self.hd_key)
            self.hd_key = tmp
            priv_key = self.hd_key.Prv_key()[1:]
            self.key_pair = k_box(priv_key.hex())
            with open(_program_dir + "/address", 'a') as f:
                f.write(f"{self.key_pair.get_address()}\n")
            print(f"key pair generated")
            print(f"extended_format")
            print(f"Private key(WIF): {wallet.to_WIF(self.key_pair.get_secret_key().hex())}")
            print(f"Address         : {self.key_pair.get_address()}")
        except Exception as e:
            print(f"Error [{e}]")
        

    def do_new_hdkey(self, msg):
        'make hd_key, [-m] - from mnemonic phrase'
        msg  = msg.split()
        testnet  = True if self.net == 0x6f else False
        if (len(msg) == 0):
            try:
                e = secrets.token_bytes(32)
                self.hd_key = bip32.bip32_key.from_entropy(entropy=e,testnet= testnet)
                print (f'mnemonic phrase:\n{bip39.mnemonic_from_entropy(e)}')
                priv_key = self.hd_key.Prv_key()[1:]
                self.key_pair = k_box(priv_key.hex())
                with open(_program_dir + "/address", 'a') as f:
                    f.write(f"{self.key_pair.get_address()}\n")
                print(f"key pair generated")
                print(f"Private key(WIF): {wallet.to_WIF(self.key_pair.get_secret_key().hex())}")
                print(f"Address         : {self.key_pair.get_address()}")
            except Exception as e:
                print (f'Error [{e}]')
                return False
        elif msg[0] == "-m":
            mnemonic = " ".join(msg[1:])
            try:
                e = bip39.entropy_from_mnemonic(mnemonic)
                self.hd_key = bip32.bip32_key.from_entropy(entropy= e ,testnet=testnet)
                print (f'mnemonic phrase:\n{bip39.mnemonic_from_entropy(e)}')
                priv_key = self.hd_key.Prv_key()[1:]
                self.key_pair = k_box(priv_key.hex())
                with open(_program_dir + "/address", 'a') as f:
                    f.write(f"{self.key_pair.get_address()}\n")
                print(f"key pair generated")
                print(f"Private key(WIF): {wallet.to_WIF(self.key_pair.get_secret_key().hex())}")
                print(f"Address         : {self.key_pair.get_address()}")
            except Exception as e:
                print (f'Error [{e}]')
                return False


    def do_new(self, inp):
        'Make new key pair'
        if self.key_pair != 0:
            print("Already there is key pair, if continue it would be deleted. Continue ? (n/y):")
            if input() == "n":
                return False
        try:
            self.key_pair = k_box(net = self.net)
            with open(_program_dir + "/address", 'a') as f:
                f.write(f"{self.key_pair.get_address()}\n")
            print(f"key pair generated")
            print(f"Private key(WIF): {wallet.to_WIF(self.key_pair.get_secret_key().hex())}")
            print(f"Address         : {self.key_pair.get_address()}")
            return False
        except Exception as e:
            print (f'Error: [{e}]')
            return False

    
    def do_import(self, file_path):
        if self.key_pair != 0:
            print("Already there is key pair, if continue it would be deleted. Continue ? (n/y):")
            if input() == "n": 
                return False
        file_path= file_path.strip()
        try:
            self.key_pair = wallet.f_import_private(file_path, net=self.net)
            with open(_program_dir + "/address", 'a') as f:
                f.write(f"{self.key_pair.get_address()}\n")
        except Exception as error:
            print(error)
            return False
        print(f"Private key(WIF): {wallet.to_WIF(self.key_pair.get_secret_key().hex())}")        
        print(f"Address         : {self.key_pair.get_address()}")

    # def do_on(self, args):
    #     # self.do_import("minerkey")
    #     self.do_test_send("mtjD4ptoT2XToLcefZH7fYZYjKq3CDpvTM 11500000")


    def do_broadcast(self, args):
        for tx in self.transactions:
            try:
                rq = requests.post(self.server_ip + '/transaction/new', data=tx)
                if rq.status_code:
                    print (rq.text)
                    self.transactions.remove(tx)
                else:
                    print("Error sending to pull")
            except Exception:
                print ("Server unavalible")

    
    def do_send(self, args):
        if self.key_pair == 0:
            print("Haven`t key pair")
            return False
        split = args.strip().split(' ')
        if (not args or len(split) != 2):
            print("Please input  [Recipient Address] [Amount]")
            return False
        t_recip, t_amount = split
        if t_recip == '-s':
            self.transactions.append(t_amount)
            return False
        t_amount = int(t_amount)
        try:
        # if True:
            self.update_unspend_pool()
            sum_of_inp, prev_outputs = self.get_outputs(t_amount)
            inputs = [Input(txid=bytearray.fromhex(txid), vout=vout) for txid, vout, o in prev_outputs]
            outputs = [Output(recipient=t_recip, value=t_amount)]
            if sum_of_inp - t_amount > FEE:
                change = sum_of_inp - t_amount - FEE
                outputs.append(Output(self.key_pair.get_address(), value=(change)))
            tx = Transaction(inputs, outputs)
            tx.sign_tx(prev_outputs, self.key_pair)
            s_tx = Serializer.serialize(tx)
            print(s_tx)
            self.transactions.append(s_tx)
        except Exception as identifier:
            print (f'Error:[{identifier}]')
        return False


    def update_unspend_pool(self):
        if self.key_pair == 0:
            raise Exception("Haven`t key pair")
        rq = requests.post(self.server_ip + '/utxo/get_uout', data=self.key_pair.get_address())        
        utxo = json.loads(rq.text)
        self.unspend_pool =[(tx, vout, Deserializer.deserialize_output(o)[0]) for tx, vout, o in utxo]
        self.unspend_pool.sort(key=lambda outp: outp[-1].value)

    def get_outputs(self, value):
        'return sum and list of tuples:(txid, vout, output)'
        result_sum = 0
        n = 0
        for o in self.unspend_pool:
            result_sum += o[-1].value
            n += 1
            if result_sum > value:
                break
        if result_sum <= value:
            raise Exception("Have not enuf money")
        return (result_sum, self.unspend_pool[:n])

    def do_get_unspend(self,value):
        try:
            self.update_unspend_pool()
            for i in  self.unspend_pool:
                print(f'__txid: {bytearray.fromhex(i[0])[::-1].hex()}[{i[1]}]\n     _value: {i[2].value}')
        except Exception as identifier:
            print (f'Error:[{identifier}]')



    def do_getbalance(self, args):
        try:
            print(self.key_pair.get_address())
            rq = requests.post(self.server_ip + '/utxo/getbalance', data=self.key_pair.get_address())
            print(rq.text)
        except Exception:
            print ("Server unavalible")
        return False


#%%:
def main():
    wallet_cli().cmdloop()
    print("Stoped")


if __name__ == "__main__":
    main()    
    
