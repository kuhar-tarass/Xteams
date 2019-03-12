#%%:
import sys
sys.path.append("/Users/tkuhar/X.Teams/module_1/pitcoin")
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
        result = quee[0:3]
        s.close()
    with open("mempool", 'w') as s:
        s.writelines(quee[3:])
        s.close()
    return result

#%%:
# add_tx("0002012awQNWFJkBaNmr6L9NC4PXCNbNcy836CL016Ten288ANg6DsAWKbkPNRQ5W6NxU52hzJ27719104399e5765def1a156bbf2b445a92adc1a3dfb676e56afbdba28a31264d599d2f72dd5a00a3d7b219a21e70e18953a7b55d81f2706fedb926d13da97dab056aa3087a051984d7dd648c03d6a36caacdb2caf366774fbd43478c8bac492567e496d28d834a953055f155b1c32246397dcee6a19a63b2a140153bab8a9c8")
# import json
# print(json.dumps('\u1234'))
# 000101M1DJ6Ws2SopbqbA4BxvXqJFmm45PQopUh001to4yvjbUSJvUYKJ6JertB7nUBJvJEQXG042d8acca8d8f31640d8277b15c1cef050042aaad95e98fcc46835d37d6635a511a9332b9bc7581a3fa525992a600e096497e7a1d2e03e1ba373d69aa52f6948e77e4e6165ffa02f76cefef7bc8f6ac329e70179d32c118ae7684df2d1620a14634e2e75cbad5bd26a003a48c8c12048ccfb5351067886ccb37d58acc38091b0b3
# 042d8acca8d8f31640d8277b15c1cef050042aaad95e98fcc46835d37d6635a511a9332b9bc7581a3fa525992a600e096497e7a1d2e03e1ba373d69aa52f6948
# 0002012awQNWFJkBaNmr6L9NC4PXCNbNcy836CL016Ten288ANg6DsAWKbkPNRQ5W6NxU52hzJ27719104399e5765def1a156bbf2b445a92adc1a3dfb676e56afbdba28a31264d599d2f72dd5a00a3d7b219a21e70e18953a7b55d81f2706fedb926d13da97dab056aa3087a051984d7dd648c03d6a36caacdb2caf366774fbd43478c8bac492567e496d28d834a953055f155b1c32246397dcee6a19a63b2a140153bab8a9c8
# 042d8acca8d8f31640d8277b15c1cef050042aaad95e98fcc46835d37d6635a511a9332b9bc7581a3fa525992a600e096497e7a1d2e03e1ba373d69aa52f6948
#%%
