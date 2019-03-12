# import hashlib
from hashlib import sha256 , new as ripemd160
import var_int
from wallet import k_box
import wallet
import ecdsa
#%%:
class Input:
    def __init__(self, txid = 0, vout = 0):
        self.txid = txid               #? 32 bytes (revers)
        self.vout = vout               #? 4 bytes (revers)
        self.scriptsigsize = 0
        self.scriptsig = 0              #?    bytearray       
        self.ss_sign = 0                  #? bytearray
        self.ss_pubkey = 0
        self.sequence = 0xffffffff.to_bytes(4,'big')           #? 4 bytes (revers)

    def sign_input(self, key:k_box = 0):
        """hash this tx with scriptsig == script_pub_key previous tx"""
        # msg = sha256(sha256( "hash this tx with scriptsig == script_pub_key previous tx" ).digest()).digest()
        # sk = ecdsa.SigningKey.from_string(key.get_secret_key())
        # self.ss_sign = sk.sign(msg, sigencode=ecdsa.util.sigencode_der)
        # self.ss_pubkey = key.get_public_key_compresed()
        # self.scriptsig = f'{Serializer.varint(len(self.ss_sign) + 1)}{self.ss_sign.hex()}01\
        #                    {Serializer.varint(len(self.ss_pubkey))}{self.ss_pubkey.hex()}'
        # self.scriptsigsize = len(self.scriptsig) // 2
        pass

        

    
class Output:
    """recipient accept addres in base58 format """
    def __init__(self, recipient:str = 0, value = 0):
        self.value = value                  #? 8 bytes (revers)
        self.recipient_address = recipient
        self.script_pub_key = self.p2pkh(recipient)
        self.script_pub_key_size = len(self.script_pub_key)    #? var 

    def p2pkh(self,recipient):
        hash160 = wallet.base58_decode(recipient).hex()
        l = var_int.int_to_varint(len(hash160))
        scriptPubKey = (f"76a9{l}{hash160}88ac")
        return scriptPubKey



class Transaction:
    def __init__(self, inputs = [], outputs = []):
        self.version = 1                     #? 4 bytes (revers)
        self.input_count = len(inputs)                #? varINT
        self.inputs = inputs
        self.output_count = len(outputs)                #? varINT
        self.outputs= outputs
        self.locktime = 0                   #? 4 bytes (revers)

    def txid(self) -> bytearray:           # ? must be reversed for using in input
        from serializer import Serializer
        chksum = sha256(sha256(bytearray.fromhex(Serializer.serialize(self))).digest()).digest()
        return chksum


class CoinbaseTransaction(Transaction):
    def __init__(self, recipient:str = 0, value = 0):
        inputs = [Input(txid=bytearray.fromhex("0000000000000000000000000000000000000000000000000000000000000000"), vout=0xffffffff)]
        inputs[0].sign_input()
        outputs = [Output(recipient=recipient, value=value)]
        Transaction.__init__(self,inputs=inputs, outputs=outputs)
