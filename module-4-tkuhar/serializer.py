#%%:
from transaction import Transaction, Input, Output
import var_int
import json


# %%:
class Serializer:
    @staticmethod
    def serialize(tx: Transaction) -> str:
        result =\
            f"{tx.version.to_bytes(4, byteorder='little').hex()}"\
            f"{var_int.int_to_varint(tx.input_count)}"
        for i in tx.inputs:
            result += Serializer.serialize_input(i)
        result +=\
            f"{var_int.int_to_varint(tx.output_count)}"
        for o in tx.outputs:
            result += Serializer.serialize_output(o)
        result +=\
            f"{tx.locktime.to_bytes(4, byteorder='little').hex()}"
        return result


    @staticmethod
    def serialize_input(i: Input) -> str:
        result =\
            f"{i.txid.hex()}"\
            f"{i.vout.to_bytes(4,'little').hex()}"\
            f"{var_int.int_to_varint(i.scriptsigsize)}"\
            f"{i.scriptsig}"\
            f"{i.sequence[::-1].hex()}"
        return result

    @staticmethod
    def serialize_output(o: Output) -> str:
        result =\
            f"{o.value.to_bytes(8, byteorder='little').hex()}"\
            f"{var_int.int_to_varint(o.script_pub_key_size)}"\
            f"{o.script_pub_key}"
        return result
    
    @staticmethod
    def serialize_output_json(o: Output) -> str:
        o.script_pub_key = o.script_pub_key
        return json.dumps(o.__dict__)


class Deserializer:
    @staticmethod
    def deserialize(s) -> Transaction:
        tx = Transaction()
        tx.version = int.from_bytes(bytearray.fromhex(s[0:8]), byteorder = "little")
        s = s[8:]
        tx.input_count, v_int = var_int.varint_to_int(s)
        s = s[v_int:]
        for i in range(0,tx.input_count):
            inp , padd = Deserializer.deserialize_input(s)
            tx.inputs.append(inp)
            s = s[padd:]
        tx.output_count, v_int = var_int.varint_to_int(s)
        s = s[v_int:]
        for i in range (0, tx.output_count):
            otp, padd = Deserializer.deserialize_output(s)
            tx.outputs.append(otp)            
            s = s[padd:]
        return tx


    @staticmethod
    def deserialize_input(s):
        padd = 0
        r_i = Input()
        r_i.txid = (bytearray.fromhex(s[0:64]))                                 #?txid
        padd += 64
        s = s[64:]
        r_i.vout = int.from_bytes(bytearray.fromhex(s[0:8]), byteorder='little')#?vout
        padd += 8
        s = s[8:]
        r_i.scriptsigsize, v_int = var_int.varint_to_int(s)                     #?sript sig size
        padd += v_int
        s = s[v_int:]
        r_i.scriptsig = s[0:r_i.scriptsigsize * 2]                              #? script sig
        padd += r_i.scriptsigsize * 2
        s = s[r_i.scriptsigsize * 2:]
        r_i.sequence = bytearray.fromhex(s[0:8])[::-1]                          #? sequence 
        padd += 8 
        return (r_i, padd)
    
    
    @staticmethod
    def deserialize_output(s):
        'return output and it`s n chars'
        padd = 0
        r_o = Output()
        r_o.value = int.from_bytes(bytearray.fromhex(s[0:16]), byteorder='little')  #? value
        padd += 16
        s = s[16:]
        r_o.script_pub_key_size, v_int = var_int.varint_to_int(s)               #? script pub_key size
        padd += v_int
        s = s[v_int:]
        r_o.script_pub_key = s[0:r_o.script_pub_key_size * 2]                   #? script pub_key
        padd += r_o.script_pub_key_size * 2
        return (r_o, padd)

    @staticmethod
    def deserialize_output_json(j_output):       
        o = Output()
        o.value = int(j_output['value'])
        o.recipient_address =  bytearray.fromhex(j_output['recipient'])
        o.script_pub_key = j_output['script_pub_key']
        o.script_pub_key_size = int (j_output['script_pub_key_size'])
        return o

#%%:

# if __name__ == "__main__":
#     tx = Deserializer.deserialize("0200000000010144d3c9d6686d9c297093d1f166b1fc6c14f677e50592467bd8ef5ec48d6e7d18040000001716001418c3062dc7968fae59c8424472ce63b4e38981e7feffffff0210bf07000000000017a9146837ddaacaccd91cf1c5a30d49c16f8931e1399487001bb700000000001976a91490eaf52d7d998bb47eaa6d74fa1f81214f643a5a88ac0247304402202a492b5735fedc875da7d30b707107e77a3d6e3873c0b6cc8d3ec09668ba58f8022079970b4199c4d2780a24658f981e1d5740ef3986ee88214c30f1a10b077f5944012103a13f96fc3bd33d634f0c85e17bd5011c8eb91240a884e007c3284b73c949e340be381600")
#     import pprint 
#     pprint.pprint(tx.outputs[0].__dict__)

#%%
