from transaction import Transaction
#%%:
class Serializer:
    @staticmethod
    def serialize(transaction:Transaction) -> str:
        if len(f"{transaction.amount:04x}") > 4 : raise Exception ("Amount is too big")    # ! too small amount length
        result = f"{transaction.amount:04x}"\
                 f"{transaction.sender.rjust(35, '0')}"\
                 f"{transaction.recipient.rjust(35, '0')}"\
                 f"{transaction.sender_pubkey[1:].hex()}"\
                 f"{transaction.sign.hex()}"                                    
        return result                     
                

#%%:
class Deserializer:
    @staticmethod
    def deserialize(str) -> Transaction:
        if len(str) != 330: raise Exception ("Broken data") 
        t = Transaction()
        t.amount = int(str[0:4])
        t.sender = str[4:39].lstrip('0')
        t.recipient = str[39:74].lstrip('0')
        t.sender_pubkey = 0x04.to_bytes(1,byteorder="big") + bytearray.fromhex(str[74:202])
        t.sign = bytearray.fromhex(str[202:])
        return t
    

#%%
