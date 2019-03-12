#%%:
import sys
# sys.path.append("/Users/tkuhar/X.Teams/module_1/pitcoin")
from serializer import Deserializer
import tx_valiadtor
import transaction
import os.path
import json


#%%:
def add_tx(s):
    t = Deserializer.deserialize(s)
    tx_valiadtor.check_tx(t)
    with open((os.path.abspath(".") + "/mempool"), 'a+') as f:
        f.write(f"{s}\n")
        f.close()


#%%:
def get_last_tx():
    with open("mempool", 'r') as s:
        quee = s.readlines()
        result = [i.rstrip() for i in quee[0:3]]
        s.close()
    with open("mempool", 'w') as s:
        s.writelines(quee[3:])
        s.close()
    return result
