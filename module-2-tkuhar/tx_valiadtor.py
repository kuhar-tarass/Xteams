from transaction import Transaction
import wallet
from hashlib import sha256
import ecdsa


def check_tx(tx: Transaction) -> bool:
    # enc_rec = wallet.base58_decode(tx.recipient)
    # checksum = sha256(sha256(enc_rec[0:21]).digest()).digest()
    # if checksum[0:4] != enc_rec[-4:]:
    #     raise Exception(f"Non valide recipient address {enc_rec}")
    # if tx.sender != 34*'0':
    #     if wallet.covert_to_address(tx.sender_pubkey) != tx.sender:
    #         raise Exception("Non valide sender addres")
    # ver_key = ecdsa.VerifyingKey.from_string(
    #     tx.sender_pubkey[1:], curve=ecdsa.SECP256k1)
    # if not ver_key.verify(tx.sign, tx.hash()):
    #     raise Exception("Not valid sign")
    return True
