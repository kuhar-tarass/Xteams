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
            f"{i.txid[::-1].hex()}"\
            f"{i.vout.to_bytes(4,'little').hex()}"\
            f"{var_int.int_to_varint(i.scriptsigsize)}"\
            f"{i.scriptsig}"\
            f"{i.sequence[::-1].hex()}"
        return result

    @staticmethod
    def serialize_output(o: Output) -> str:
        result =\
            f"{bytearray.fromhex(f'{o.value:016x}')[::-1].hex()}"\
            f"{var_int.int_to_varint(o.script_pub_key_size)}"\
            f"{o.script_pub_key}"
        return result
    
    @staticmethod
    def serialize_output_json(o: Output) -> str:
        o.script_pub_key = o.script_pub_key.hex()
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
        r_i.txid = (bytearray.fromhex(s[0:64]))[::-1]                               #?txid
        padd += 64
        s = s[64:]
        r_i.vout = int.from_bytes(bytearray.fromhex(s[0:8]), byteorder='little')    #?vout
        padd += 8
        s = s[8:]
        r_i.scriptsigsize, v_int = var_int.varint_to_int(s)                           #?sript sig size
        padd += v_int
        s = s[v_int:]
        r_i.scriptsig = s[0:r_i.scriptsigsize * 2]                                  #? script sig
        padd += r_i.scriptsigsize * 2
        s = s[r_i.scriptsigsize * 2:]
        r_i.sequence = bytearray.fromhex(s[0:8])[::-1]                              #? sequence 
        padd += 8 
        return (r_i, padd)
    
    
    @staticmethod
    def deserialize_output(s):
        padd = 0
        r_o = Output()
        r_o.value = int.from_bytes(bytearray.fromhex(s[0:16]), byteorder='little')  #? value
        padd += 16
        s = s[16:]
        r_o.script_pub_key_size, v_int = var_int.varint_to_int(s)                     #? script pub_key size
        padd += v_int
        s = s[v_int:]
        r_o.script_pub_key = s[0:r_o.script_pub_key_size * 2]                       #? script pub_key
        padd += r_o.script_pub_key_size * 2
        a_len , v_int = var_int.varint_to_int(r_o.script_pub_key[5:7])
        r_o.recipient_address = r_o.script_pub_key[5 + v_int: a_len]            #? p2pkh getting addres from 
        return (r_o, padd)

    @staticmethod
    def deserialize_output_json(j_output):       
        o = Output()
        o.value = int(j_output['value'])
        o.recipient_address =  bytearray.fromhex(j_output['recipient'])
        o.script_pub_key = j_output['script_pub_key']
        o.script_pub_key_size = int (j_output['script_pub_key_size'])
        return o

