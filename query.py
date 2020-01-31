import asyncio
import sys
import os
from .utils.bencoder import *
from .utils.tools import RandomArgs, extract_nodes, random_node_id
import logging
from .utils.ping import Ping
from .client import BitClientProtocol
from .db.models import ValidNodes, TargetNodes, TorrentInfo
from .db.controller import DHTDatabase

DHT_ROUTER = "67.215.246.10"
DHT_PORT = 6881
MAX_RETRY = 3

# for memo
# NAT Traversal
# https://tools.ietf.org/html/rfc5389


class DHTQuery(object):
    def __init__(self, node_id=None, info_hash=None):
        self.payload = dict()
        self.random = None
        if node_id and info_hash:
            self.random = RandomArgs(node_id, info_hash)
        elif node_id or info_hash:
            self.random = RandomArgs(node_id) if node_id else RandomArgs(None, info_hash)
        else:
            self.random = RandomArgs()
        self.protocol = BitClientProtocol
        self.controller = DHTDatabase(
            os.getenv('DB_USER', 'postgres'),
            os.getenv('DB_PASSWORD', '0584qwqw'),
            os.getenv('DB_NAME', 'dht_database')
        )

    def ping(self, dest=(DHT_ROUTER, DHT_PORT)):
        arg_dict = {"id": self.random.node_id}

        self.prepare_payload("ping", arg_dict)

        # logging.info(self.payload)
        return asyncio.run(self.send(dest))

    def find_node(self, dest=(DHT_ROUTER, DHT_PORT), target=None):
        arg_dict = {
            "id": self.random.node_id,
            "target": None,
        }
        if target:
            arg_dict["target"] = target if isinstance(target, bytes) else bytes.fromhex(target)
        else:
            arg_dict["target"] = self.random.node_id

        self.prepare_payload("find_node", arg_dict)
        # logging.info(self.payload)

        return asyncio.run(self.send(dest))

    def get_peers(self, dest=(DHT_ROUTER, DHT_PORT), info_hash=None):
        arg_dict = {
            "id": self.random.node_id,
            "info_hash": self.random.info_hash if not info_hash else info_hash,
        }

        self.prepare_payload("get_peers", arg_dict)
        # logging.info(self.payload)

        return asyncio.run(self.send(dest))

    def announce_peer(self, dest, info_hash, token, port=None):
        arg_dict = {
            "id": self.random.node_id,
            "info_hash": info_hash,
            "implied_port": 0,
            "port": 6881 if not port else port,  # not fixed
            "token": token,  # for test #token
        }
        self.prepare_payload("announce_peer", arg_dict)

        return asyncio.run(self.send(dest))

    def prepare_payload(self, request_type, args):
        # self.random._generate_tid()

        self.payload["t"] = self.random.transaction_id
        self.payload["y"] = "q"  # class only for query
        self.payload["q"] = request_type
        self.payload["a"] = args

        # self.payload = bencode(self.payload)

    async def send(self, target_addr):
        assert isinstance(target_addr, tuple)
        loop = asyncio.get_running_loop()

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: self.protocol(bencode(self.payload), loop),
            remote_addr=target_addr
        )
        try:
            await protocol.connection_end
            # z = extract_info(response[b'r'][b'nodes'])
            # print(z)
            # print(protocol.connection_end.result())
            if not protocol.connection_end.result():
                # can take error msg or return error
                logging.error("Error Occured!")
            # handle Error
            else:
                response = bdecode(protocol.response)
                print(response)
                return response

        except:
            logging.error(f"Error : {sys.exc_info()}")
            transport.close()
    '''
    def bootstrap or query_sequence(self):
        1. ping -- get node id
        2. find_node
            2.1 ping to nodes -- get alive nodes
        3. get_peers
            3.1 max checks ~= 32 (if info hash does not exist anywhere (or close nodes))
            3.2 if get token goto 4 else regenerate info hash (about 2~3 times)
            3.3 (maybe) known info hash needs
        4. announce_peer (if got token)
        -- need to check peer protocol for check file info
    '''

    def collect_nodes(self, dest, target=None):
        # find nodes and health check --> insert to DB
        if not target:
            # DB select
            pass
        for i in range(MAX_RETRY):
            response = self.find_node(dest, target)
            if response: break
        if not response:
            logging.warning(f"Request find_node to {dest} is not available now.")
            return
        node_address = extract_nodes(response[b'r'][b'nodes'])
        icmp = Ping()
        enable_ip = icmp.ping_check([addr['ip'] for addr in node_address])
        target_nodes = dict()
        idx_key = 0
        for node in node_address:
            if node['ip'] in enable_ip:
                target_nodes[idx_key] = node
                idx_key += 1
        logging.info(target_nodes)
        self.controller.insert(data=[TargetNodes(
            node_id=tn['nodeid'],
            ip=tn['ip'],
            port=tn['port'],
        ) for tn in target_nodes.values()])

    def spread_nodes(self, info_hash=None):
        if not info_hash:
            info_hash = self.random.info_hash

    def test_get_peers(self, init_dest=(DHT_ROUTER, DHT_PORT), info_hash=None):
        pass


if __name__ == "__main__":
    r = logging.getLogger()
    r.setLevel(logging.INFO)
    dq = DHTQuery(node_id=b'\x9e\x92\x1e\x97"lC\xc3\x0eB\x9a&\xa3\xc2\xd3o\x89\x94\x83B') # node_id=b'2\xf5NisQ\xffJ\xec)\xcd\xba\xab\xf2\xfb\xe3F|\xc2g'
    target = random_node_id()
    dq.collect_nodes(dest=(DHT_ROUTER, DHT_PORT), target=target)
    # b'2\xf5NisQ\xffJ\xec)\xcd\xba\xab\xf2\xfb\xe3F|\xc2g'
    # x = dq.find_node()

    # # print(x)
    # if not x: sys.exit(0)
    # addr_list = extract_nodes(x['r'.encode()]['nodes'.encode()])
    # check = Ping()
    # print(addr_list)
    # enables = check.ping_check([x['ip'] for x in addr_list])
    # print("enables: ", enables)
    # enable_ip = list()
    #
    # ip_and_ports = list()
    # for addr in addr_list:
    #     if addr['ip'] in enables:
    #         ip_and_ports.append(addr)

    # print(ip_and_ports)
    # for d in ip_and_ports:
    #     t = dq.get_peers(dest=(d["ip"], d["port"]), info_hash=b'T\x86\x12W\xc3\xefj\x01x\xd2\x984`\nN\xf1\xe1\xc6!@')
    #     print(d["ip"], d["port"])
    #     if not t: continue
    #     print("----------- Announce Peer -----------")
    #     tk = t[b'r'][b'token']
    #     print(tk)
    #     dq.announce_peer((d["ip"], d["port"]), info_hash=b'T\x86\x12W\xc3\xefj\x01x\xd2\x984`\nN\xf1\xe1\xc6!@',
    #                      token=tk)
    #     print("----------- Announce Peer Ends -----------")
