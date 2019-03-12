import requests, os
import json
# req = requests.post('http://127.0.0.1:5000/test', data=json.dumps(['123', '300', '444']))
# print (type(req.status_code))

from os import listdir
from os.path import isfile, join
# onlyfiles = [f for f in listdir('./pitcoin/chain') if isfile(join('./pitcoin/chain', f))]
f = open("./pitcoin/wallet.py", 'r+')
a = f.readlines()
# f.readline()
for i in a:
    print (i, end='')
# f.close()
# print(onlyfiles)
# class A:
#     def __init__(self):
#         self.a = 1
#         self.b = 1

# d = {"one": 1, "two": 2, "three": 3, "four": 4}
# print(d)
# print( max(d,key=d.get) )
# print( type(max(d) ))
# print ( json.dumps(a.__dict__ ))