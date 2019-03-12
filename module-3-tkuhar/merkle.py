from hashlib import sha256


def merkle_root(txs: list):
    a = [sha256(sha256(i.encode()).digest()).digest() for i in txs]
    return up_tree(a).hex()


def merge(a, b):
    return sha256(sha256(a + b).digest()).digest()


def up_tree(hash_arr: list):
    if len(hash_arr) > 0 and len(hash_arr) % 2 == 1:
        hash_arr.append(hash_arr[-1])
    if len(hash_arr) > 2:
        a = [merge(hash_arr[i], hash_arr[i + 1])
             for i in range(0, len(hash_arr), 2)]
        return (up_tree(a))
    else:
        return merge(hash_arr[0], hash_arr[-1])
