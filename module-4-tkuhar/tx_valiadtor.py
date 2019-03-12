from transaction import Transaction, Input, Output
import wallet
from hashlib import sha256
import ecdsa
from script import script_vm


def check_tx(tx: Transaction, outputs=0) -> bool:
    if outputs == 0:
        return True
    else:
        for i in tx.inputs:
            if   i.txid.hex() == 64*'0':
                return True
            get_lockscript = lambda p_outputs, txid: [j for j in p_outputs if j[0] == txid][0][-1].script_pub_key
            # tmp = tx
            digest = tx.get_digest_for_sign_input(i, outputs)
            # print(i.scriptsig , get_lockscript(outputs,i.txid.hex()) ,digest.hex())
            unlock = script_vm().parse_script(i.scriptsig , get_lockscript(outputs,i.txid.hex()) ,digest)
            if unlock == False:
                return False
        return True



    
