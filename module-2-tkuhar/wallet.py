#!/usr/bin/env python
# coding: utf-8

#%%:
import secrets
import hashlib
import base64
import ecdsa
from sys import byteorder


#%%:
class k_box:
    def __init__(self, string = 0, file = 0):
        if string != 0:
            if not(len(string) == 64):
                raise Exception("Bad len")
            self.__priv_key = bytes.fromhex(string)
        else:
            self.__priv_key = secrets.randbits(256).to_bytes(32,byteorder=byteorder)
        self.__pub_key = ecdsa.SigningKey.from_string(self.__priv_key, curve=ecdsa.SECP256k1).verifying_key.to_string()

        
    def get_secret_key(self):
        return self.__priv_key

    
    def get_public_key(self)->bytearray:
        return (0x04.to_bytes(1,byteorder=byteorder) + self.__pub_key)


    def get_public_key_compresed(self) -> bytearray:
        return (b'\x03' if self.__pub_key[-1] % 2 else b'\x02') + self.__pub_key[0:32]
    
    
    def get_address(self) -> str:
        e_pub = self.get_encrypted_pub_key()
        main_net_key = 0x00.to_bytes(1,byteorder=byteorder) + e_pub
        check_sum = hashlib.sha256(hashlib.sha256(main_net_key).digest()).digest()[:4]
        hex_addr = main_net_key + check_sum
        return base58_encode(hex_addr)

    def get_encrypted_pub_key(self):
        sha = hashlib.sha256(self.get_public_key_compresed()).digest()
        result = hashlib.new(name='ripemd160', data=sha).digest()    
        return result
    
    
    def sign(self, message:bytes = 0) -> bytearray:
        sk = ecdsa.SigningKey.from_string(self.__priv_key, curve=ecdsa.SECP256k1 )
        return sk.sign(message)

    
    def verify(self, signature, message):
        vk = ecdsa.VerifyingKey.from_string(self.__pub_key, curve=ecdsa.SECP256k1)
        return vk.verify(signature, message.encode())        
    


#%%:
def covert_to_address(pub_key:bytes) -> str:
    sha = hashlib.sha256(pub_key).digest()
    pub_key = hashlib.new(name='ripemd160', data=sha).digest()    
    main_net_key = 0x00.to_bytes(1,byteorder=byteorder) + pub_key
    check_sum = hashlib.sha256(hashlib.sha256(main_net_key).digest()).digest()[:4]
    hex_addr = main_net_key + check_sum
    return base58_encode(hex_addr)


#%%:
def base58_encode(n:bytearray)->str:
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    b58_string = ""
    leading_zeros = len(n.hex()) - len(n.hex().lstrip('0'))                     # ! refactor counting zeros
    address_int = int.from_bytes(n,byteorder="big")
    while address_int > 0:
        digit = address_int % 58
        digit_char = alphabet[digit]
        b58_string = digit_char + b58_string
        address_int //= 58
    ones = leading_zeros // 2
    for one in range(ones):
        b58_string = '1' + b58_string
    return b58_string

def base58_decode(s):
    """Decode a base58-encoding string, returning bytes"""
    if not s:
        return b''
    alphabet =  '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    # Convert the string to an integer
    n = 0
    for c in s:
        n *= 58
        if c not in alphabet:
            raise Exception('Character %r is not a valid base58 character' % c)
        digit = alphabet.index(c)
        n += digit

    # Convert the integer to bytes
    h = '%x' % n
    if len(h) % 2:
        h = '0' + h
    # res = ""
    res =  bytearray.fromhex(h)

    # Add padding back.
    pad = 0
    for c in s[:-1]:
        if c == alphabet[0]: pad += 1
        else: break
    return b'\x00' * pad + res



# def base58_decode(s:str, len):
#     alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
#     result = 0
#     for c in s:
#         result = result * 58 + alphabet.index(c)
#     return bytearray.fromhex(f"{result:0x}".rjust(len * 2, '0'))

# %%:
def to_WIF(key:str):
    if not(len(key) == 64):
        raise Exception("Bad key len")
    key = "80" + key
    key_b = bytes.fromhex(key)
    sha_key1 = hashlib.sha256(hashlib.sha256(key_b).digest()).digest()
    key_b = key_b + sha_key1[0:4]
    return base58_encode(key_b)


def f_import_private(filename):
    file = open(filename, 'r')
    wif_key = file.read()
    file.close()
    key = from_WIF(wif_key)
    key_pair = k_box(string=key.hex())
    return key_pair


#%%:
def from_WIF(wif_key):
    if not(len(wif_key) == 51):
        raise Exception("Bad len of WIF key")
    key = base58_decode(wif_key)
    checksum = key[-4:]
    key = key[1:33]
    if hashlib.sha256(hashlib.sha256(0x80.to_bytes(1,"big") + key).digest()).digest()[0:4] != checksum:
        raise Exception("Bad checksum")
    return key

#%%:

def uncompress_key(comp_key:  bytearray):
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