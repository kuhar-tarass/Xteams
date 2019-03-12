#%%:
import hashlib
import ecdsa
import math
# 
#%%:
class script_vm:
    def __init__(self):
        self.stack = []
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
        print(f"_in_f_____{sig.hex()}")
        if vk.verify( signature=sig, data=self.tx_hash , sigdecode=ecdsa.util.sigdecode_der):
            self.stack.append(b'\x01')
        else:
            self.stack.append(b'\x00')
        print(f"________________________________________________---{self.stack[-1]}")
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
        print(f"__OP_EQUALVERIFY__:{self.stack[-1].hex(), self.stack[-2].hex()}")
        if self.stack.pop() == self.stack.pop():
            return True
        else:
            return False
    
    def parse_script(self, s, sig, pubKey, tx_hash) -> bool:
        self.tx_hash = tx_hash
        self.stack.append(sig)
        self.stack.append(pubKey)
        skip = 0
        i = len(s)
        while i > 0:
            # self.get_out_stack()
            if skip:
                self.stack.append(bytearray.fromhex(s[:skip*2]))
                s = s[(skip * 2 - 2):]
                i-= (skip * 2 - 2)
                skip = 0
            elif s[0:2] in self.func:
                if not self.func[s[0:2]]():
                    return False
            else:
                skip = int(s[0:2],16)
            s = s[2:]
            i -= 1
        return True if self.stack[-1] == '\x01' else False

#%%:
def uncompress_key(comp_key:  bytearray):
        assert len(comp_key) == 33, "bad len of key"
        x = int.from_bytes(comp_key[1:], byteorder='big')
        is_even = True if comp_key[1] == '2' else False
        """ Derive y point from x point """
        curve = ecdsa.SECP256k1.curve
        # The curve equation over F_p is:
        #   y^2 = x^3 + ax + b
        a, b, p = curve.a(), curve.b(), curve.p()
        alpha = (pow(x, 3, p) + a * x + b) % p
        beta = ecdsa.numbertheory.square_root_mod_prime(alpha, p)
        if (beta % 2) == is_even:
            beta = p - beta
        return bytearray.fromhex( f"04{x:064x}{beta:064x}")

#%%:
import ecdsa
from hashlib import sha256
sk = ecdsa.SigningKey.from_string(bytearray.fromhex("9df5a907ff17ed6a4e02c00c2c119049a045f52a4e817b06b2ec54eb68f70079"), curve=ecdsa.SECP256k1)


tx = "01000000018190374a5a1feb54fab4417fac1a3d9185de06fd8dcac34822c7cd00083638b1000000001976a914977ae6e32349b99b72196cb62b5ef37329ed81b488acffffffff02c8550f00000000001976a9140964c6feb963ade6836e722670abbc0147ca5cec88ac88660700000000001976a914977ae6e32349b99b72196cb62b5ef37329ed81b488ac00000000"
or_sign = "483045022100c395d12ba577a34fdbb918ec59705a2b9ec6743a85c75ecf4e22524342230b540220361a373ec88fc5ddb5045ba8f8c047c8d738f11a6e83d2bf67bc8634de8038e7012103c13dca192f1ba64265d8efca97d43b822ff24db357c13b0e6e0395cf91e9efae"





sign_message = sha256(sha256(bytearray.fromhex(tx)).digest()).digest()[::-1]

script_sig = "47304402200aa5891780e216bf1941b502de29890834a2584eb576657e340d1fa95f2c0268022010712e05b30bfa9a9aaa146927fce1819f2ec6d118d25946256770541a8117b6012103d2305c392cbd5ac36b54d3f23f7305ee024e25000f5277a8c065e12df5035926"
# script_sig = "47304402204e572c0587b2147efaa5685b470350bad9561c359056ecb2abb0eca05bc612f502203aae1b45aa24215b2575a26871f18c95fb1b911eaed7705eaf53cb3a2b031ea0012103c13dca192f1ba64265d8efca97d43b822ff24db357c13b0e6e0395cf91e9efae"
# own_kakaha=  "30450220146f03f415a221f99921162c1c2e34761df39a015c4b13b6bdb35c2dfc750f3a022100a2bb6edca55d5f7b454c714e7bc57034254da37de01a40eb486ca1a37d7ab711"

sig = script_sig[2:(int(script_sig[0:2],16)*2 + 2)]
print(f"_____SIG:{sig}")
sig  = bytearray.fromhex(sig)
script_sig = script_sig[len(sig)*2 + 2:]
# script_sig = script_sig[:-2]

print(script_sig)
pub_key = script_sig[2:(int(script_sig[0:2],16)*2 + 2)]
print(f"_____pubkey:{pub_key}")
pub_key = bytearray.fromhex(pub_key)
# print(pub_key)

# 3046022100ee32be71ec8ed3df66373720218d6b5f2a360153760a4192a517d04e76e6607c022100c9b7bb415ce1009aaf7d934e472991ae913400b6d9975011faf8cdda8552e95f
# 304402204e572c0587b2147efaa5685b470350bad9561c359056ecb2abb0eca05bc612f502203aae1b45aa24215b2575a26871f18c95fb1b911eaed7705eaf53cb3a2b031ea001
# print(f"pub_key______{pub_key.hex()}")
# sign_m_original = "b138360800cdc72248c3ca8dfd06de85913d1aac7f41b4fa54eb1f5a4a379081"
# sign_m_original = bytearray.fromhex(sign_m_original)[::-1].hex()
# 03c13dca192f1ba64265d8efca97d43b822ff24db357c13b0e6e0395cf91e9ef


# print (f"__out_f___{sk.sign(sign_message,  sigencode=ecdsa.util.sigencode_der).hex()}")
# print (sign_message.hex())
# print(sig)
unlock = "76a9143bbebbd7a3414f9e5afebe79b3b408bada63cde288ac"
a = script_vm().parse_script(unlock, sig, pub_key, sign_message)
print(f"#####################{a}#####################")


# a4bfa8ab6435ae5f25dae9d89e4eb67dfa94283ca751f393c1ddc5a837bbc31b
# 76 a9 14   0964c6feb963ade6836e722670abbc0147ca5cec 88 ac
# 30440220576497b7e6f9b553c0aba0d8929432550e092db9c130aae37b84b545e7f4a36c022066cb982ed80608372c139d7bb9af335423d5280350fe3e06bd510e695480914f01
# 30440220576497b7e6f9b553c0aba0d8929432550e092db9c130aae37b84b545e7f4a36c022066cb982ed80608372c139d7bb9af335423d5280350fe3e06bd510e695480914f01
#%%
# 1b45aa24215b2575a26871f18c95fb1b911eaed7705eaf53cb3a2b031ea0012103c13dca192f1ba64265d8efca97d43b822ff24db357c13b0e6e0395cf91e9efae
# 03c13dca192f1ba64265d8efca97d43b822ff24db357c13b0e6e0395cf91e9efae
# 03c13dca192f1ba64265d8efca97d43b822ff24db357c13b0e6e0395cf91e9efae
#%%
