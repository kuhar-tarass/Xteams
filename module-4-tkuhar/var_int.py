def int_to_varint(i):
    if i <= 0xfc:
        return f"{i.to_bytes(1,byteorder='little').hex()}"
    elif i <= 0xffff:
        return f"fd{i.to_bytes(2,byteorder='little').hex()}"
    elif i <= 0xffffffff:
        return f"fe{i.to_bytes(4,byteorder='little').hex()}"
    else:
        return f"ff{i.to_bytes(8,byteorder='little').hex()}"


def varint_to_int(s):
    """return: (int, n_chars used for this int)"""
    if s[0:2] == 'ff':
        return int.from_bytes(bytearray.fromhex(s[2:18]), byteorder='little') , 18
    elif s[0:2] == 'fe':
        return int.from_bytes(bytearray.fromhex(s[2:10]), byteorder='little') , 10 
    elif s[0:2] == 'fd':
        return int.from_bytes(bytearray.fromhex(s[2:6]), byteorder='little') , 6
    else:
        # print(f'----------------------------------------------------{s}----------------------------------------------------')
        return  int.from_bytes(bytearray.fromhex(s[0:2]), byteorder='little') , 2