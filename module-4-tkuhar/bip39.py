import hashlib
from hashlib import sha256
import wordlist
import hmac

def mnemonic_from_entropy(entropy:bytearray):
    if len(entropy) not in [16, 20, 24, 28, 32]:
        raise Exception('Bad len of entropy')        
    chk_sum = sha256(entropy).digest()
    chk_sum_b = bin(int.from_bytes(chk_sum, 'big'))[2:].zfill(256)
    words_b = bin(int.from_bytes(entropy,'big'))[2:].zfill(len(entropy) * 8)
    data_bit_str = words_b + chk_sum_b[:len(entropy) * 8 // 32]
    phrase = []
    for i in range(len(data_bit_str) // 11):
        word = int(data_bit_str[ i*11 : (i+1)*11 ], 2)
        phrase.append(wordlist.words[word])
    res = " ".join(phrase)
    return res

def entropy_from_mnemonic(mnemonic:str):
    words = mnemonic.split(' ')
    if len(words) not in [12, 15, 18, 21, 24]:
        raise Exception(f'Number of words must be one of the following: [12, 15, 18, 21, 24], but it is not ({len(words)})')

    bits = ''
    for word in words:
        try:
            idx = wordlist.words.index(word)
            bits += bin(idx)[2:].zfill(11)[-11:]
        except ValueError:
            raise Exception(f'Unable to find "{word}" in word list.')
    bits_chk_sum = bits[-(len(bits)%32):]
    bits_entropy = bits[:-(len(bits)%32)]
    entropy = int(bits_entropy,2).to_bytes(len(bits_entropy)//8, 'big')
    chk_sum = sha256(entropy).digest()
    if (bin(int.from_bytes(chk_sum,'big'))[2:].zfill(256))[:len(bits)%32] != bits_chk_sum:
        raise Exception(f'Bad chksum')
    return (entropy)

if __name__ == "__main__":
    entropy = bytearray.fromhex('c880cb643f6f5368418041f0d7432b91c76cd4ea442ee1f98e15972fae4d05cc')
    a = mnemonic_from_entropy(entropy)
    print (a)
    a= "thunder curve area evoke divorce depend rent city toilet pizza craft stuff such goat suggest behind shove wrong lyrics lounge clutch hero feel network"
    ent = entropy_from_mnemonic(a)
    print (ent.hex())
    print (hmac.HMAC(ent, b'' , digestmod='sha512').digest().hex())

    
# 41063a4d8c43cc2bc6008ab061760516c00e3ed2c8d1ea9c6cca7d43ddd5595d47e257e2362fcdddeb1408959c0acb9097de6ee6d67d2d046709cff60812ed56