import sys
import uuid
import hashlib
import os
import codecs

STATIC_PORT = 6881


class RandomArgs(object):
    # Random Generate Objects such as node_id, info_hash, transaction_id
    def __init__(self, nid=None, ih=None, tid=None):
        self.hf = hashlib.sha1()
        # self.ihf = hashlib.sha1()
        self._info_hash = self._generate_ih() if not ih else ih
        self._generate_tid() if not tid else tid
        # self._generate_nid() if not nid else bytes.fromhex(nid)
        if not nid:
            self._generate_nid()
        else:
            self.node_id = nid if isinstance(nid, bytes) else bytes.fromhex(nid)
        self._generate_ih() if not ih else ih

    def _generate_tid(self):
        random_tid = uuid.uuid4().hex[0:2]
        self._transaction_id = random_tid

    def _generate_nid(self):
        random_str = uuid.uuid4().hex
        self.hf.update(random_str.encode())

        # format of hex string to hex bytes
        self.node_id = bytes.fromhex(self.hf.hexdigest())

    def _generate_ih(self):
        random_str = uuid.uuid4().hex
        self.hf.update(random_str.encode())
        self._info_hash = bytes.fromhex(self.hf.hexdigest())

    @property
    def node_id(self):
        return self._node_id

    @node_id.setter
    def node_id(self, nid):
        self._node_id = nid

    @property
    def info_hash(self):
        return self._info_hash

    @info_hash.setter
    def info_hash(self, ih):
        self._info_hash = ih

    @property
    def transaction_id(self):
        self._generate_tid()
        return self._transaction_id


def random_node_id():
    random_str = uuid.uuid4().hex
    hash_func = hashlib.sha1()
    hash_func.update(random_str.encode())
    return bytes.fromhex(hash_func.hexdigest())


def convert(value, mode):
    # to bytes / to str
    if mode == 'b':
        return bytes.fromhex(value)
    elif mode == 's':
        return value.hex()
    else:
        print("Error: mode argument must be 'b' or 's'", file=sys.stderr)
        sys.exit(0)


# use for find_nodes
def extract_nodes(nodes):
    node_list = [nodes[x:x + 26] for x in range(0, len(nodes), 26)]
    info_dict = {}

    def extract_detail(value):
        assert isinstance(value, list)
        idx = 0
        for v in value:
            d = {
                'ip': '.'.join(['{}'.format(x) for x in v[20:24]]),
                'port': int.from_bytes(v[24:], 'big'),
                'node_id': v[0:20] # convert(v[0:20], 's')
            }
            info_dict[str(idx)] = d
            idx += 1
        return info_dict

    return _nodes_to_list(extract_detail(node_list))


def _nodes_to_list(node_dict):
    # form : {'ip': blah, 'port': blah, 'nodeid': blahblah}
    node_list = list()
    for key in node_dict:
        node_list.append(node_dict[key])
    return node_list


def get_distance(origin, remote):
    result = b''
    for i in range(len(origin)):
        result += bytes([origin[i] ^ remote[i]])
    bin_result = bin(int.from_bytes(result, 'big'))
    return bin_result.count('1')


def get_hash(filename):
    # filename is based on --current-- root file directory
    # /utils X -> /
    # torrent file info hash is consist of many 20-bit info hashes(e.g., ubuntu live --> 20 * 1696 )
    current_path = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(current_path, '../', filename)
    with codecs.open(filepath, 'rb') as f:
        from .bencoder import bdecode
        content = bdecode(f.read())
        piece = content[b'info'][b'pieces']
    length = content[b'info'][b'length']
    piece_length = content[b'info'][b'piece length']
    # return first 20-bit for test
    return piece[0:20], [piece[i:i+20] for i in range(0, (length // piece_length) * 20, 20)]


if __name__ == '__main__':
    # get_hash("ubuntu-18.04.3-live-server-amd64.iso.torrent")
    pass
