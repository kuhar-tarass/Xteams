# import hashlib
from hashlib import sha256 , new as ripemd160
import var_int
from wallet import k_box
import wallet
import ecdsa
import secrets
from copy import deepcopy

class Input:
    def __init__(self, txid = 0, vout = 0):
        self.txid = txid
        self.vout = vout
        self.scriptsigsize = 0
        self.scriptsig = 0
        self.ss_sign = 0
        self.ss_pubkey = 0
        self.sequence = 0xffffffff.to_bytes(4,'big')
    
    def sign_input(self, sign:bytearray,  pubkey:bytearray):
        'pubkey must be in compresed form'
        self.ss_sign = sign
        self.ss_pubkey = pubkey
        self.scriptsig =\
              var_int.int_to_varint(len(sign + b'\x01')) + sign.hex()+ b'\x01'.hex()\
            + var_int.int_to_varint(len(pubkey)) + pubkey.hex()
        self.scriptsigsize = len(self.scriptsig) // 2


class Output:
    'recipient accept addres in base58 format '
    def __init__(self, recipient:str = 0, value = 0):
        self.value = value                  #? 8 bytes (revers)
        self.script_pub_key =  self.p2pkh(recipient) if recipient else ""
        self.script_pub_key_size = len(self.script_pub_key) // 2    #? var 

    def p2pkh(self,recipient):
        hash160 = wallet.convert_from_address(recipient)
        l = var_int.int_to_varint(len(hash160))
        scriptPubKey = (f"76a9{l}{hash160.hex()}88ac")
        return scriptPubKey
    
    @property
    def recipient_address(self):
        if self.script_pub_key == "":
            return ""
        a_len , v_int = var_int.varint_to_int(self.script_pub_key[4:])
        hex160 =  bytearray.fromhex(self.script_pub_key[(4 + v_int): (a_len * 2 + (4 + v_int))])
        return wallet.covert_to_address(hex160=hex160, net=0x6f)                                            #! net identificator


class Transaction:
    def __init__(self, inputs = [], outputs = []):
        self.version = 1
        self.input_count = len(inputs)
        self.inputs = inputs.copy()
        self.output_count = len(outputs)
        self.outputs= outputs.copy()
        self.locktime = 0

    def txid(self) -> bytearray:
        from serializer import Serializer
        chksum = sha256(sha256(bytearray.fromhex(Serializer.serialize(self))).digest()).digest()
        return chksum

    def sign_tx(self, prew_outputs, keys:k_box):
        'private_key in bytearray'
        inputs_signs = []
        sk = ecdsa.SigningKey.from_string(keys.get_secret_key(), curve=ecdsa.SECP256k1)
        pub_k = keys.get_public_key_compresed()
        for i in range(self.input_count):
            tx_digest = self.get_digest_for_sign_input(i,prew_outputs)
            i_sign = sk.sign_digest(digest=tx_digest, sigencode=ecdsa.util.sigencode_der_canonize)
            inputs_signs.append(i_sign)
        for i in range(self.input_count):
            self.inputs[i].sign_input(inputs_signs[i], pub_k)

    def get_digest_for_sign_input(self, input_index, prew_outputs)->bytearray:
        from serializer import Serializer        
        get_pubkey = lambda p_outputs, txid: [i for i in p_outputs if i[0] == txid][0][-1].script_pub_key
        tmp0 = self.inputs
        self.inputs = [deepcopy(i) for i in self.inputs]
        for j in range(self.input_count):
                if j == input_index:
                    self.inputs[j].scriptsig = get_pubkey(prew_outputs, self.inputs[j].txid.hex())
                    self.inputs[j].scriptsigsize = len(self.inputs[j].scriptsig) // 2
                else:
                    self.inputs[j].scriptsig = ""
                    self.inputs[j].scriptsigsize = 0
        serialized_tx = bytearray.fromhex(Serializer.serialize(self))  + (1).to_bytes(4, byteorder='little')
        self.inputs = tmp0
        return sha256(sha256(serialized_tx).digest()).digest()


class CoinbaseTransaction(Transaction):
    def __init__(self, recipient:str = 0, value = 0):
        inputs = [Input(txid=bytearray.fromhex("0000000000000000000000000000000000000000000000000000000000000000"), vout=0xffffffff)]
        inputs[0].scriptsig = ((f"Kill_me_pls").encode("utf-8") + secrets.token_bytes(10)).hex()
        inputs[0].scriptsigsize = len(inputs[0].scriptsig) // 2
        outputs = [Output(recipient=recipient, value=value)]
        Transaction.__init__(self,inputs=inputs, outputs=outputs)