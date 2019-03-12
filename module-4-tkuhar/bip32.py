#%%
import ecdsa
import hmac
import hashlib
import secrets
import b58


#%%:
N = ecdsa.curves.SECP256k1.order #!?! ???
MAINNET_PRV = (0x0488ADE4).to_bytes(4,'big')
MAINNET_PUB = (0x0488B21E).to_bytes(4,'big')
TESTNET_PRV = (0x04358394).to_bytes(4,'big')
TESTNET_PUB = (0x043587CF).to_bytes(4,'big')
BIP32_HARDEN    = 0x80000000 # choose from hardened set of child keys
# N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
# k = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1).to_string()
# a = hmac.HMAC(key = k, msg = bytes(10), digestmod='sha512').digest()
class bip32_key:
    @staticmethod
    def from_entropy(entropy:bytearray=None, public= False, testnet= False):
        if entropy == None:
            entropy = secrets.token_bytes(16)
        if not len(entropy) >= 16:
            raise Exception('Bad len of entropy')
        I = hmac.HMAC(key = b'Bitcoin seed', msg = entropy, digestmod='sha512').digest()
        Il, Ir = I[:32], I[32:]
        key = bip32_key(secret = Il, chain = Ir, depth = 0, index = 0, finger_p= 0x00000000.to_bytes(4,'big'), public=False, testnet=testnet)
        if public is True:
            key.k = None
            key.public = True
        return key
    
    @staticmethod
    def from_xpub(xkey, public= False):
        raw = b58.check_decode(xkey)
        if len(raw) != 78:
            raise Exception("extended key format wrong length")
        version = raw[0:4]
        if version == MAINNET_PRV:
            is_testnet = False
            is_pub_only = False
        elif version == MAINNET_PUB:
            is_testnet = False
            is_pub_only = True
        elif version == TESTNET_PRV:
            is_testnet = True
            is_pub_only = False
        elif version == TESTNET_PUB:
            is_testnet = True
            is_pub_only = True
        else:
            raise Exception('Can`t recognize fromat')


        depth = raw[4]
        fp = raw[5:9]
        index = int.from_bytes(raw[9:13], 'big')
        chain = raw[13:45]
        secret = raw[45:78]

        if not is_pub_only:
            secret = secret[1:]
        else:
            lsb = secret[0] & 1 if type(secret[0]) == int else ord(secret[0]) & 1
            x = int.from_bytes(secret[1:], byteorder= 'big')
            ys = (x**3+7) % N # y^2 = x^3 + 7 mod p
            y = ecdsa.numbertheory.square_root_mod_prime(ys, N)
            if y & 1 != lsb:
                y = N-y
            point = ecdsa.ellipticcurve.Point(ecdsa.SECP256k1.curve, x, y)
            secret = ecdsa.VerifyingKey.from_public_point(point, curve=ecdsa.SECP256k1)
        key = bip32_key(secret,chain,depth,index,fp,public=is_pub_only, testnet=is_testnet)
        if not is_pub_only and public:
            key.k = None
            key.public = True
        return key


    def __init__(self, secret, chain, depth, index, finger_p,  public=False, testnet=False):
        self.public = public
        if public is False:
            self.k = ecdsa.SigningKey.from_string(secret, curve = ecdsa.SECP256k1)
            self.K = self.k.get_verifying_key()
        else:
            self.k = None
            self.K = secret
        self.C = chain
        self.depth = depth
        self.finger_p = finger_p
        self.testnet = testnet
        self.index = index


    def derivation(self, index):
        if self.public is False:
            return self.CKDpriv(index)
        else:
            return self.CKDpub(index)


    def fingerp(self):
        identifier = hashlib.new('ripemd160', hashlib.sha256(self.Pub_key()).digest()).digest()
        fp = identifier[:4]
        return fp


    def Pub_key(self):
        'return compresed publick key '
        K_x = self.K.to_string()[:32]
        byte =  b'\x03' if self.K.pubkey.point.y() & 1  else b'\x02'
        return byte + K_x 

    def Prv_key(self):
        if self.public:
            raise Exception('can`t get privat key from hardnes derevation')
        else:
            return b'\x00' + self.k.to_string()

    def hmac(self, msg):
        I = hmac.HMAC(key = self.C, msg = msg, digestmod='sha512').digest()
        return I


    def CKDpriv(self, i):
        '''Private parent key → private child key'''
        i_str = i.to_bytes(length = 4, byteorder= 'big')

        if i >= 2**31:
            I = self.hmac(msg=b'\x00' + self.k.to_string() + i_str)
        else:
            I = self.hmac(msg= self.Pub_key() + i_str)
            # l = f_hmac(key = c_par,msg=ser_256(k_par) + ser_32(i)
        Il, Ir = I[0:32], I[32:64]

        k_i = (int.from_bytes(Il,'big') + int.from_bytes(self.k.to_string(), 'big')) % N
        if (k_i == 0):
            return None
        c_i = Ir
        return bip32_key(secret = k_i.to_bytes(32,'big'), chain = c_i, depth=self.depth + 1, index = self.index, finger_p = self.fingerp(), testnet= self.testnet)


    def CKDpub(self, i):
        '''Public parent key → public child key\n
        Exdended public key '''
        i_str = i.to_bytes(length = 4, byteorder= 'big')
        if i >= 2**31:
            raise Exception('Cannot create a hardened child key using public child derivation')
        else:
            I = self.hmac(msg = self.Pub_key() + i_str)
        Il = I[0:32]
        Ir = I[32:64]
        Il_int = int.from_bytes(Il, 'big')
        point = Il_int*ecdsa.SECP256k1.generator + self.K.pubkey.point
        K_i = ecdsa.VerifyingKey.from_public_point(point, curve=ecdsa.SECP256k1)
        c_i = Ir
        return bip32_key(secret = K_i, chain = c_i, depth= self.depth + 1, index = self.index, finger_p = self.fingerp(),  public=True, testnet=self.testnet)
    

    def Identifier(self):
        "Return key identifier as string"
        cK = self.Pub_key()
        return hashlib.new('ripemd160',hashlib.sha256(cK).digest()).digest()


    def Address(self):
        "Return compressed public key address"
        addressversion = b'\x00' if not self.testnet else b'\x6f'
        vh160 = addressversion + self.Identifier()
        return b58.check_encode(vh160)


    def Ext_format(self, privat = True, encode=b58.check_encode):
        ' import key in extended format (privat = False for public key )\n encode -> function to encode'
        if self.public and privat:
            raise Exception('Cannot get priv key from public only det_key')
        if not self.testnet:
            version = MAINNET_PRV if privat else MAINNET_PUB
        else:
            version = TESTNET_PRV if privat else TESTNET_PUB 
        if privat == False or self.public == True:
            data = self.Pub_key()
        else:
            data = b'\x00' + self.k.to_string()

        raw = version\
            + self.depth.to_bytes(1,"big")\
            + self.finger_p\
            + self.index.to_bytes(4, "big")\
            + self.C\
            + data
        if encode == None:
            return raw
        else:
            return encode(raw)


    def dump(self):
        "Dump key fields mimicking the BIP0032 test vector format"
        print("   * Identifier")
        # print("     * (hex):      ", b2a_hex(self.Identifier()))
        print("     * (fpr):      ", self.fingerp().hex())
        print("     * (main addr):", self.Address())
        if self.public is False:
            print("   * Secret key")
            print("     * (hex):      ", self.k.to_string().hex())
            # print("     * (wif):      ", self.WalletImportFormat())
        print("   * Public key")
        print("     * (hex):      ", self.Pub_key().hex())
        print("   * Chain code")
        print("     * (hex):      ", self.C.hex())
        print("   * Serialized")
        print("     * (pub hex):  ", self.Ext_format(privat=False).hex())
        print("     * (prv hex):  ", self.Ext_format(privat=True).hex())
        print("     * (pub b58):  ", self.Ext_format(privat=False, encode=b58.check_encode))
        print("     * (prv b58):  ", self.Ext_format(privat=True, encode=b58.check_encode))


def chain(s:str, base_key):
    ' m - master , h -hardned derevation, '
    key = base_key
    chain = s.split('/')
    if chain[0] != 'm':
        raise Exception('Bad Chain')
    else:
        chain.remove('m')
    for node in chain:
        if node[-1] == 'h':
            key= key.derivation(int(node[:-1] , 10) + BIP32_HARDEN)
        elif node.isalnum():
            key= key.derivation(int(node, 10))
        else:
            raise Exception("Bad chain")
        # print(chain[chain.index(node):])
        # key.dump()
    return key

        




#%%:



if __name__ == "__main__":
    def test_1():
        entropy = bytearray.fromhex('000102030405060708090A0B0C0D0E0F')
        m = bip32_key.from_entropy(entropy)
        print("Test vector 1:")
        print("Master (hex):", entropy.hex())
        print("* [Chain m]")
        m.dump()
        print("* [Chain m/0h]")
        m = m.derivation(0+BIP32_HARDEN)
        m.dump()

        print("* [Chain m/0h/1]")
        m = m.derivation (1)
        m.dump()

        print("* [Chain m/0h/1/2h]")
        m = m.derivation (2+BIP32_HARDEN)
        m.dump()

        print("* [Chain m/0h/1/2h/2]")
        m = m.derivation (2)
        m.dump()

        print("* [Chain m/0h/1/2h/2/1000000000]")
        m = m.derivation (1000000000)
        m.dump()

    def test_2():
        # BIP0032 Test vector 2
        entropy = bytearray.fromhex('fffcf9f6f3f0edeae7e4e1dedbd8d5d2cfccc9c6c3c0bdbab7b4b1aeaba8a5a29f9c999693908d8a8784817e7b7875726f6c696663605d5a5754514e4b484542')
        m = bip32_key.from_entropy(entropy)
        print("Test vector 2:")
        print("Master (hex):", entropy.hex())
        print("* [Chain m]")
        m.dump()

        print("* [Chain m/0]")
        m = m.derivation (0)
        m.dump()

        print("* [Chain m/0/2147483647h]")
        m = m.derivation (2147483647+BIP32_HARDEN)
        m.dump()

        print("* [Chain m/0/2147483647h/1]")
        m = m.derivation (1)
        m.dump()

        print("* [Chain m/0/2147483647h/1/2147483646h]")
        m = m.derivation (2147483646+BIP32_HARDEN)
        m.dump()

        print("* [Chain m/0/2147483647h/1/2147483646h/2]")
        m = m.derivation (2)
        m.dump()    

    def test_3():
        entropy = bytearray.fromhex('fffcf9f6f3f0edeae7e4e1dedbd8d5d2cfccc9c6c3c0bdbab7b4b1aeaba8a5a29f9c999693908d8a8784817e7b7875726f6c696663605d5a5754514e4b484542')
        m = bip32_key.from_entropy(entropy)
        m.dump()
        key = chain("m/0/2147483647h/1/2147483646h/2",m)
        key.dump()    

    def test_4():
        import bip39
        e = bip39.entropy_from_mnemonic("soccer someone matter modify later deposit audit coil tortoise bottom album input library enact vehicle anxiety sample pulse soda another arrest ask special trick")
        m = bip32_key.from_entropy(e)
        key = chain("m/0/0", m)
        key.dump()

    # test_1()
    # test_2()
    # test_3()
    test_4()
# print(N)
# #%%
# def point_p(p):
#     priv_key_str = p.to_bytes(32,'big')
#     sk = ecdsa.SigningKey.from_string(priv_key_str)
#     pk = sk.get_verifying_key().to_string()
#     return int.from_bytes(pk)

# def ser_32(i:int):
#     return i.to_bytes(length = 4, byteorder= 'big')


# def ser_256(i:int):
#     return i.to_bytes(length = 32, byteorder= 'big' )


# def ser_p(p):
#     'p  -- byte representation of public key'
#     byterep = p.to_bytes(64, byteorder='big')
#     x = byterep[0:32]
#     y = byterep[32:]
#     res = b'\x02' if  y & 1 else b'\x03' + x
#     return res


# def parse256(p:bytearray):
#     return int.from_bytes(p,'big')

# def f_hmac(key,msg)->bytearray:
#     return hmac.HMAC(key,msg,digestmod='sha512').digest()



# def CKDpriv(k_par:int,c_par, i) -> (int,bytearray):
#     '''Private parent key → private child key\n
#     k_par -- normal privat key, c -- chain code'''
#     if i >= 2**31:
#         l = f_hmac(key = c_par,msg=b'\x00' + ser_256(k_par) + ser_32(i))
#     else:
#         l = f_hmac(key = c_par,msg=ser_256(k_par) + ser_32(i))
#     l_l = l[0:32]
#     l_r = l[32:64]
#     k_i = (parse256(l_l) + k_par) % N
#     c_i = l_r
#     return k_i, c_i


# def CKDpub(K_par:int,c_par, i):
#     '''Public parent key → public child key\n
#     Exdended public key '''
#     if i >= 2**31:
#         raise Exception('Failure')
#     else:
#         l = f_hmac(key = c_par, msg = ser_p(K_par) + ser_32(i))
#     l_l = l[0:32]
#     l_r = l[32:64]
#     K_i = point_p(parse256(l_l)) + K_par
#     c_i = l_r
#     return K_i, c_i


# def func_N(k,c): #!!!!
    
#     K = point_p(k)
    
#     return K, c

# def key_tree():
    


    

#%%
