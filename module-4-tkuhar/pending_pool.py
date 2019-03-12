#%%:
import sys
# sys.path.append("/Users/tkuhar/X.Teams/module_1/pitcoin")
from serializer import Deserializer
import tx_valiadtor
import transaction
import os.path
import json

_program_dir = os.path.dirname(os.path.abspath(__file__))
#%%:
def add_tx(s):
    t = Deserializer.deserialize(s)
    tx_valiadtor.check_tx(t)
    with open((_program_dir + "/mempool"), 'a+') as f:
        f.write(f"{s}\n")
        f.close()


#%%:
def get_last_tx():
    with open((_program_dir + "/mempool"), 'r') as s:
        quee = s.readlines()
        result = [i.rstrip() for i in quee[0:3]]
        s.close()
    with open((_program_dir + "/mempool"), 'w') as s:
        s.writelines(quee[3:])
        s.close()
    return result
