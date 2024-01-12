import asyncio
import os
from BitTorrent.utils.bencoder import *
from BitTorrent.utils.tools import RandomArgs, extract_nodes
import logging
from BitTorrent.protocols.client_protocol import DHTClientProtocol
from BitTorrent.db.models import TargetNodes, AnnouncedNodes, ValidNodes
from BitTorrent.db.controller import DHTDatabase
from BitTorrent.utils.tools import random_node_id
from BitTorrent.utils.ping import Ping
from typing import List

DHT_ROUTER = "67.215.246.10"
DHT_PORT = 6881
MAX_RETRY = 3

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
            os.getenv('DB_USER', ''),
            os.getenv('DB_PASSWORD', ''),
            os.getenv('DB_NAME', 'dht_database')
        ) if not controller else controller

    # not async method would be removed
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

    # not async method would be removed
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

    # not async method would be removed
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

    # not async method would be removed
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
            "implied_port": 0,  # not fixed (NAT?)
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

        if healthy_nodes:
            self.controller.insert(data=[TargetNodes(
                node_id=tn['node_id'],
                ip=tn['ip'],
                port=tn['port'],
            ) for tn in healthy_nodes])
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
            found_target = self.__classify(nodes)
            data_objects = [AnnouncedNodes(announced=node.id) for node in found_target]
            self.controller.insert(data_objects)
            valid_object = ValidNodes(node_id=self.random.node_id)  # self node id
            self.controller.insert(valid_object)
            return True, nodes
        else:
            return False, None

    def __classify(self, nodes: List) -> List[TargetNodes]:
        target_nodes = list()
        for node in nodes:
            result = self.controller.select_target(node['node_id'])
            if not result:
                target_node = TargetNodes(
                    node_id=node.get('node_id'),
                    ip=node.get('ip'),
                    port=node.get('port')
                )
                self.controller.insert(target_node)
                target_node = self.controller.select_target(target_node.node_id)
                target_nodes.append(target_node)
            else:
                target_nodes.append(result)
        return target_nodes

    def announce_sequence(self, target, info_hash=None):
        info_hash = self.random.info_hash if not info_hash else info_hash
        announces, _ = asyncio.run(self.__get(target, info_hash))  # get peer nodes with token
        print(announces)
        if not announces:
            return False, None
        success, failed = asyncio.run(self.__announce(announces, info_hash))
        if not success:
            return False, failed
        else:
            return True, success

    async def __get(self, target, info_hash):
        targets = list(target)
        announces = list()
        for _ in range(2):
            futures = [self.async_get_peers(dest=(t['ip'], t['port']), info_hash=info_hash) for t in targets]
            results = await asyncio.gather(*futures)
            targets.clear()  # flush previous target list
            for result in results:
                response, dest = result
                if not response or response.get(b'e'):
                    logging.warning(response)
                    continue
                if not response.get(b'r').get(b'token'):
                    print(response)
                    nodes = extract_nodes(response.get(b'r').get(b'nodes'))
                    targets.extend([n for n in nodes])
                else:
                    announces.append((dest, response.get(b'r').get(b'token')))
        return announces, targets

    async def __announce(self, announces: list, info_hash):
        # announces: __get() result
        announced = list()
        announce_failed = list()
        print(f"line 286: {announces}")

        futures = [self.async_announce_peer(target, info_hash, token) for target, token in announces]
        results = await asyncio.gather(*futures)

        for response, dest in results:
            target_dict = dict()
            target_dict['ip'], target_dict['port'] = dest
            target_dict['node_id'] = None
            if not response:
                announce_failed.append(target_dict)
            elif response.get(b'e'):
                logging.warning(response.get(b'e'))
                announce_failed.append(target_dict)
            else:
                target_dict['node_id'] = response.get(b'r').get(b'id')
                announced.append(target_dict)
        return announced, announce_failed

    async def multi_ping(self, nodes, max_retry=MAX_RETRY):
        # bittorrent ping check
        healthy_nodes = list()
        futures = [self.async_ping(dest=(tn['ip'], tn['port'])) for tn in nodes.values()]

        responses = await asyncio.gather(*futures)
        for response, dest in responses:
            if response:
                logging.info(f"{dest} : {response}")
                healthy_nodes.append(dict(
                    ip=dest[0],
                    port=dest[1],
                    node_id=response.get(b'r').get(b'id'),
                ))
        return healthy_nodes


if __name__ == "__main__":
    r = logging.getLogger()
    r.setLevel(logging.INFO)
    dq = DHTQuery(node_id=b'\x9e\x92\x1e\x97"lC\xc3\x0eB\x9a&\xa3\xc2\xd3o\x89\x94\x83B')

    resp = dq.find_node()
    addr_list = extract_nodes(resp['r'.encode()]['nodes'.encode()])
    icmp_ping = Ping()
    enables = icmp_ping.ping_check(x['ip'] for x in addr_list)

    ip_and_ports = list()
    for addr in addr_list:
        if addr['ip'] in enables:
            ip_and_ports.append(addr)

    for d in ip_and_ports:
        t = dq.get_peers(dest=(d["ip"], d["port"]), info_hash=b'T\x86\x12W\xc3\xefj\x01x\xd2\x984`\nN\xf1\xe1\xc6!@')
        logging.info(d["ip"], d["port"])
        if not t: continue
        logging.info("----------- Announce Peer -----------")
        tk = t[b'r'][b'token']
        logging.info(tk)
        res = dq.announce_peer((d["ip"], d["port"]), info_hash=b'T\x86\x12W\xc3\xefj\x01x\xd2\x984`\nN\xf1\xe1\xc6!@',
                         token=tk)
        logging.info("----------- Announce Peer Ends -----------")
