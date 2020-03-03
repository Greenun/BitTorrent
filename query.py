import asyncio
import sys
import os
from BitTorrent.utils.bencoder import *
from BitTorrent.utils.tools import RandomArgs, extract_nodes
import logging
from BitTorrent.utils.ping import Ping
from BitTorrent.protocols.client_protocol import DHTClientProtocol
from BitTorrent.db.models import TargetNodes, AnnouncedNodes
from BitTorrent.db.controller import DHTDatabase

DHT_ROUTER = "67.215.246.10"
DHT_PORT = 6881
MAX_RETRY = 3

# for memo
# NAT Traversal
# https://tools.ietf.org/html/rfc5389


class DHTQuery(object):
    def __init__(self, node_id=None, info_hash=None, controller=None):
        self.payload = dict()
        self.random = None
        if node_id and info_hash:
            self.random = RandomArgs(node_id, info_hash)
        elif node_id or info_hash:
            self.random = RandomArgs(node_id) if node_id else RandomArgs(None, info_hash)
        else:
            self.random = RandomArgs()
        self.protocol = DHTClientProtocol
        self.controller = DHTDatabase(
            os.getenv('DB_USER', 'wessup'),
            os.getenv('DB_PASSWORD', '0584qwqw'),
            os.getenv('DB_NAME', 'dht_database')
        ) if not controller else controller

    def ping(self, dest=(DHT_ROUTER, DHT_PORT)):
        arg_dict = {"id": self.random.node_id}

        payload = self.prepare_payload("ping", arg_dict)

        # logging.info(self.payload)
        return asyncio.run(self.send(dest))

    async def async_ping(self, dest=(DHT_ROUTER, DHT_PORT)):
        arg_dict = {"id": self.random.node_id}

        data = self.prepare_payload("ping", arg_dict)

        resp = await self.send(dest, data)
        return resp, dest

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
        logging.info(self.payload)

        return asyncio.run(self.send(dest))

    async def async_find_node(self, dest=(DHT_ROUTER, DHT_PORT), target=None):
        arg_dict = {
            "id": self.random.node_id,
            "target": None,
        }
        if target:
            arg_dict["target"] = target if isinstance(target, bytes) else bytes.fromhex(target)
        else:
            arg_dict["target"] = self.random.node_id

        data = self.prepare_payload("find_node", arg_dict)

        resp = await self.send(dest, data)
        return resp

    def get_peers(self, dest=(DHT_ROUTER, DHT_PORT), info_hash=None):
        arg_dict = {
            "id": self.random.node_id,
            "info_hash": self.random.info_hash if not info_hash else info_hash,
        }

        self.prepare_payload("get_peers", arg_dict)
        # logging.info(self.payload)

        return asyncio.run(self.send(dest))

    async def async_get_peers(self, dest=(DHT_ROUTER, DHT_PORT), info_hash=None):
        arg_dict = {
            "id": self.random.node_id,
            "info_hash": self.random.info_hash if not info_hash else info_hash,
        }
        data = self.prepare_payload("get_peers", arg_dict)
        resp = await self.send(dest, data)
        return resp, dest

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

    async def async_announce_peer(self, dest, info_hash, token, port=None):
        arg_dict = {
            "id": self.random.node_id,
            "info_hash": info_hash,
            "implied_port": 0,
            "port": 6881 if not port else port,  # not fixed
            "token": token,  # for test #token
        }
        data = self.prepare_payload("announce_peer", arg_dict)

        resp = await self.send(dest, data)
        return resp, dest

    def prepare_payload(self, request_type, args):
        payload = dict()

        payload["t"] = self.random.transaction_id
        payload["y"] = "q"  # class only for query
        payload["q"] = request_type
        payload["a"] = args

        return payload

    # def prepare_payload(self, request_type, args):
    #     # self.random._generate_tid()
    #
    #     self.payload["t"] = self.random.transaction_id
    #     self.payload["y"] = "q"  # class only for query
    #     self.payload["q"] = request_type
    #     self.payload["a"] = args
    #
    #     # self.payload = bencode(self.payload)
    #     return self.payload

    async def send(self, target_addr, payload=None):
        assert isinstance(target_addr, tuple)
        data = payload if payload else self.payload
        loop = asyncio.get_running_loop()
        # 0303 - max retry add
        for i in range(MAX_RETRY):
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: self.protocol(bencode(data), loop),
                remote_addr=target_addr
            )
            try:
                await protocol.connection_end
                if not protocol.connection_end.result():
                    # can take error msg or return error
                    logging.warning(f"Connection Failed: {i}")
                # handle Error
                else:
                    print(protocol.response)
                    response = bdecode(protocol.response)
                    return response
            except Exception as e:
                logging.error(f"Error : {e}")
                transport.close()

    def collect_nodes(self, dest=(DHT_ROUTER, DHT_PORT), target=None):
        # find nodes and health check --> insert to DB
        # for i in range(MAX_RETRY):
        #     response = self.find_node(dest, target)
        #     if response: break
        response = asyncio.run(self.async_find_node(dest, target))
        if not response:
            logging.warning(f"Request find_node to {dest} is not available now.")
            return
        node_address = extract_nodes(response[b'r'][b'nodes'])
        # icmp ping check
        # icmp = Ping()
        # enable_ip = icmp.ping_check([addr['ip'] for addr in node_address])
        # target_nodes = dict()
        # idx_key = 0
        # for node in node_address:
        #     if node['ip'] in enable_ip:
        #         target_nodes[idx_key] = node
        #         idx_key += 1
        target_nodes = dict()
        idx_key = 0
        for node in node_address:
            target_nodes[idx_key] = node
            idx_key += 1

        healthy_nodes = asyncio.run(self.multi_ping(target_nodes))
        # logging.info(healthy_nodes)

        # if healthy_nodes:
            # self.controller.insert(data=[TargetNodes(
            #     node_id=tn['nodeid'],
            #     ip=tn['ip'],
            #     port=tn['port'],
            # ) for tn in healthy_nodes])
        return healthy_nodes

    def spread_nodes(self, info_hash=None, random=True):
        info_hash = self.random.info_hash if not info_hash else info_hash
        # 8 nodes
        if random:
            # random 8
            target_nodes = self.controller.select_random_nodes()
        else:
            # close 8
            target_nodes = self.controller.select_close_targets(self.random.node_id)

        result, nodes = self.announce_sequence(target_nodes, info_hash)
        if result:
            data_objects = [AnnouncedNodes(announced=node) for node in nodes]
            self.controller.insert(data_objects)

    def announce_sequence(self, target, info_hash=None):
        info_hash = self.random.info_hash if not info_hash else info_hash
        announces, _ = self.__get(target, info_hash)  # get peer nodes with token
        if not announces:
            return False, None
        success, failed = self.__announce(announces, info_hash)
        if not success:
            return False, failed
        else:
            return True, success

    def __get(self, target, info_hash):
        targets = list(target)
        announces = list()
        for _ in range(2):
            for _ in range(len(targets)):
                t = targets.pop(0)
                response = asyncio.run(self.async_get_peers(dest=t, info_hash=info_hash))
                if not response:
                    continue
                if not response.get('token'):
                    nodes = extract_nodes(response.get(b'r').get(b'nodes'))
                    targets.extend([(n['ip'], n['port']) for n in nodes.values()])
                else:
                    announces.append((t, response.get('token')))
        return announces, targets

    def __announce(self, announces: list, info_hash):
        # announces: __get() result
        announced = list()
        announce_failed = list()
        for target, token in announces:
            response = asyncio.run(self.async_announce_peer(target, info_hash, token))
            if response:
                # announced.append
                announced.append(response.get(b'r').get(b'id'))
            if not response:
                announce_failed.append(target)
                continue
        return announced, announce_failed
    # def __get(self, target, info_hash):
    #     targets = list(target)
    #     announces = list()
    #     for _ in range(2):
    #         for _ in range(len(targets)):
    #             t = targets.pop(0)
    #             for _ in range(MAX_RETRY):
    #                 response = self.get_peers(dest=t, info_hash=info_hash)
    #                 if response:
    #                     break
    #             if not response:
    #                 continue
    #             if not response.get('token'):
    #                 nodes = extract_nodes(response.get(b'r').get(b'nodes'))
    #                 targets.extend([(n['ip'], n['port']) for n in nodes.values()])
    #             else:
    #                 announces.append((t, response.get('token')))
    #     return announces, targets

    # def __announce(self, announces: list, info_hash):
    #     # announces: __get() result
    #     announced = list()
    #     announce_failed = list()
    #     for target, token in announces:
    #         for _ in range(MAX_RETRY):
    #             response = self.announce_peer(target, info_hash, token)
    #             if response:
    #                 # announced.append
    #                 announced.append(response.get(b'r').get(b'id'))
    #         if not response:
    #             announce_failed.append(target)
    #             continue
    #     return announced, announce_failed

    async def multi_ping(self, nodes, max_retry=MAX_RETRY):
        # bittorrent ping check
        healthy_nodes = list()
        futures = [self.async_ping(dest=(tn['ip'], tn['port'])) for tn in nodes.values()]

        responses = await asyncio.gather(*futures)
        for response, dest in responses:
            if response:
                healthy_nodes.append(dict(
                    ip=dest[0],
                    port=dest[1],
                    node_id=response.get(b'r').get(b'id'),
                ))
        return healthy_nodes
    # def multi_ping(self, nodes, max_retry=MAX_RETRY):
    #     # bittorrent ping check
    #     healthy_nodes = list()
    #     for tn in nodes.values():
    #         for _ in range(max_retry):
    #             resp = self.ping(dest=(tn['ip'], tn['port']))
    #             if resp:
    #                 healthy_nodes.append(tn)
    #                 break
    #     return healthy_nodes


if __name__ == "__main__":
    r = logging.getLogger()
    r.setLevel(logging.INFO)
    dq = DHTQuery(node_id=b'\x9e\x92\x1e\x97"lC\xc3\x0eB\x9a&\xa3\xc2\xd3o\x89\x94\x83B') # node_id=b'2\xf5NisQ\xffJ\xec)\xcd\xba\xab\xf2\xfb\xe3F|\xc2g'
    # target = random_node_id()
    # dq.collect_nodes(dest=(DHT_ROUTER, DHT_PORT), target=target)

    # b'2\xf5NisQ\xffJ\xec)\xcd\xba\xab\xf2\xfb\xe3F|\xc2g'
    x = dq.find_node()

    # print(x)
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
    #
    # print(ip_and_ports)
    # for d in ip_and_ports:
    #     t = dq.get_peers(dest=(d["ip"], d["port"]), info_hash=b'T\x86\x12W\xc3\xefj\x01x\xd2\x984`\nN\xf1\xe1\xc6!@')
    #     print(d["ip"], d["port"])
    #     if not t: continue
    #     print("----------- Announce Peer -----------")
    #     tk = t[b'r'][b'token']
    #     print(tk)
    #     res = dq.announce_peer((d["ip"], d["port"]), info_hash=b'T\x86\x12W\xc3\xefj\x01x\xd2\x984`\nN\xf1\xe1\xc6!@',
    #                      token=tk)
    #     print("----------- Announce Peer Ends -----------")
