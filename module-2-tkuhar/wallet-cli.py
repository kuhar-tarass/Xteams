# %%:
# import sys
# sys.path.append("/Users/tkuhar/X.Teams/module_1/pitcoin")
import cmd, sys, os.path, requests
import wallet
from wallet import k_box
import tx_valiadtor
from transaction import Transaction, Input, Output
from serializer import Serializer , Deserializer


# %%:
class wallet_cli(cmd.Cmd):
    intro = 'Welcome to the wallet-cli shell.   Type help or ? to list commands.\n'
    prompt = '(wallet-cli)$ '
    server_ip = "http://127.0.0.1:5000"
    key_pair = 0
    transactions = []


    def do_exit(self, inp):
        return True

    
    def do_new(self, inp):
        'Make new key pair'
        if self.key_pair != 0:
            print("Already there is key pair, if continue it would be deleted. Continue ? (n/y):")
            if input() == "n":
                return False
        print(f"key pair generated")
        self.key_pair = k_box()
        print(f"Private key(WIF): {wallet.to_WIF(self.key_pair.get_secret_key().hex())}")
        print(f"Address         : {self.key_pair.get_address()}")

    
    def do_import(self, file_path):
        if self.key_pair != 0:
            print("Already there is key pair, if continue it would be deleted. Continue ? (n/y):")
            if input() == "n": 
                return False
        file_path= file_path.strip()
        try:
            self.key_pair = wallet.f_import_private(file_path)
            with open(os.path.abspath(".") + "/address", 'a') as f:
                f.write(self.key_pair.get_address())
        except Exception as error:
            print(error)
            return False
        print(f"Private key(WIF): {wallet.to_WIF(self.key_pair.get_secret_key().hex())}")        
        print(f"Address         : {self.key_pair.get_address()}")


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
        # try:
        #     t_i = Input(txid="fffffff",vout = 0)
        #     # t_i = 
        #     # t_o = 
        #     t = Transaction( )
        #     t.sender = self.key_pair.get_address()
        #     t.sender_pubkey = self.key_pair.get_public_key()
        #     t.sign = self.key_pair.sign(t.hash())
        #     tx_valiadtor.check_tx(t)
        #     s_t = Serializer.serialize(t)
        #     self.transactions.append(s_t)

        # except Exception as identifier:
        #     print (identifier)
    

    def calculate(self, outputs, value):
        result_sum = 0
        n = 0
        sort_outputs = outputs.sort(key=lambda outp: outp.value)
        for o in sort_outputs:
            result_sum += o.value
            n += 1
            if result_sum > value:
                break
        return (outputs[:n])

    def do_getbalance(self, args):
        try:
            rq = requests.post(self.server_ip + '/getbalance', data=self.key_pair.get_address())
            print(rq.text)
        except Exception:
            print ("Server unavalible")
        return False

# ? get public key(WIF) from file  named ```privkey```
# ? save address to file named ```address```

#%%:
def main():
    wallet_cli().cmdloop()
    print("Stoped")


if __name__ == "__main__":
    main()    
    

#%%
