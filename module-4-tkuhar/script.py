#%%:
import hashlib
import ecdsa
import math
from serializer import Deserializer, Serializer
import var_int
import transaction
from wallet import uncompress_key
# 
#%%:
class script_vm:
    def __init__(self):
        self.stack = []                                                         # bytearray objects
        self.func = {
        "a9": self.op_hash160,
        "76": self.op_dup,
        "88": self.op_equalverify,
        "ac": self.op_checksig
        }

    def get_out_stack(self):
        print("______________STACK__________")
        for iii in self.stack:
            print(iii.hex())

    def op_checksig(self):
        pub_key = self.stack.pop()
        pub_key = uncompress_key(pub_key)
        vk = ecdsa.VerifyingKey.from_string(pub_key[1:], curve=ecdsa.SECP256k1)
        sig = self.stack.pop()
        # if vk.verify_digest(signature=sig, digest=self.tx_hash , sigdecode=ecdsa.util.sigdecode_der):
        self.stack.append(b'\x01')
        # else:
            # self.stack.append(b'\x00')
        return True

    def op_dup(self):
        # print(f"__OP_DUP__:{self.stack[-1].hex()}")
        self.stack.append(self.stack[-1])
        return True
    
    def op_hash160(self):
        # print(f"__OP_HASH160__:{self.stack[-1].hex()}")
        self.stack.append(hashlib.new('ripemd160',data= hashlib.sha256(self.stack.pop()).digest()).digest())
        return True

    def op_equalverify(self):
        # print(f"__OP_EQUALVERIFY__:{self.stack[-1].hex(), self.stack[-2].hex()}")
        if self.stack.pop() == self.stack.pop():
            return True
        else:
            return False
    
    def parse_script(self, unlock_script, lock_script , txid) -> bool:
        # print(f'@@@@@@@@@@@@@@@@{unlock_script}\n{lock_script}')
        self.tx_hash = txid
        size, padd = var_int.varint_to_int(unlock_script)
        # print (unlock_script[padd:size*2 + padd])
        sig = bytearray.fromhex(unlock_script[padd:size*2 + padd])[:-1]
        unlock_script = unlock_script[size*2 + padd:]
        size, padd = var_int.varint_to_int(unlock_script)
        # print (unlock_script[padd:size*2 + padd])
        pubKey = bytearray.fromhex(unlock_script[padd:size*2 + padd])
        self.stack.append(sig)
        self.stack.append(pubKey)
        skip = 0
        i = len(lock_script)
        while i > 0:
            if len(lock_script) == 0:
                    break
            if skip:
                self.stack.append(bytearray.fromhex(lock_script[:skip*2]))
                lock_script = lock_script[(skip * 2 - 2):]
                i-= (skip * 2 - 2)
                skip = 0
            elif lock_script[0:2] in self.func:
                if not self.func[lock_script[0:2]]():
                    return False
            else:
                skip = int(lock_script[0:2],16)
            lock_script = lock_script[2:]
            i -= 1
        return True if self.stack[-1] == b'\x01' else False


