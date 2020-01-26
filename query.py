import asyncio
import sys
from utils.bencoder import *
from utils.tools import RandomArgs, extract_nodes
from utils.ping import Ping
from client import BitClientProtocol

DHT_ROUTER = "67.215.246.10"
DHT_PORT = 6881

'''class BitQueryProtocol:
	def __init__(self, query, loop):
		self.query = query
		self.loop = loop

	def connection_made(self, transport):
		self.transport = transport
		#self.transport.sendto()
	def datagram_received(self, data, addr):

		self.transport.close()

	def connection_lost(self):
		pass

if __name__ == "__main__":
	loop = asyncio.get_event_loop()
	query = 'ping'
	connect = loop.create_datagram_endpoint(
	    lambda: BitQueryProtocol(query, loop),
	    remote_addr=(DHT_ROUTER, DHT_PORT))
	transport, protocol = loop.run_until_complete(connect)
	#loop.run_forever()
	transport.close()
	loop.close()'''


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

    def ping(self, dest=(DHT_ROUTER, DHT_PORT)):
        arg_dict = {"id": self.random.node_id}

        self.prepare_payload("ping", arg_dict)

        print(self.payload)
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
        # print(self.payload)

        return asyncio.run(self.send(dest))

    def get_peers(self, dest=(DHT_ROUTER, DHT_PORT), info_hash=None):
        arg_dict = {
            "id": self.random.node_id,
            "info_hash": self.random.info_hash if not info_hash else info_hash,
        }

        self.prepare_payload("get_peers", arg_dict)
        print(self.payload)

        return asyncio.run(self.send(dest))

    def announce_peer(self, dest, info_hash, target):
        pass

    def prepare_payload(self, request_type, args):
        self.random._generate_tid()

        self.payload["t"] = self.random.transaction_id
        self.payload["y"] = "q"  # class only for query
        self.payload["q"] = request_type
        self.payload["a"] = args

        # print(self.payload)

        self.payload = bencode(self.payload)

    async def send(self, target_addr):
        assert isinstance(target_addr, tuple)
        loop = asyncio.get_running_loop()

        transport, protocol = await loop.create_datagram_endpoint(
            lambda: self.protocol(self.payload, loop),
            remote_addr=target_addr
        )
        try:
            await protocol.connection_end
            # z = extract_info(response[b'r'][b'nodes'])
            # print(z)

            if not protocol.connection_end.result():
                # can take error msg or return error
                print("Error Occured!")
            # handle Error

            else:
                response = bdecode(protocol.response)
                print(response)
                return response

        except:
            print(f"Error : {sys.exc_info()}")
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

    def test_sequence(self):
        pass

    def test_get_peers(self, init_dest=(DHT_ROUTER, DHT_PORT), info_hash=None):
        pass


if __name__ == "__main__":
    dq = DHTQuery(node_id=b'F"D\xad>\xba70\xda\xa0\xacT\xc1](\xd7C\x8c\xca\x9a')
    # dq.ping()
    x = dq.find_node()

    addr_list = extract_nodes(x['r'.encode()]['nodes'.encode()])
    check = Ping()
    print(addr_list)
    enables = check.ping_check([x['ip'] for x in addr_list])

    enable_ip = list()
    for e in enables:
        enable_ip.append(e[0])

    ip_and_ports = list()
    for addr in addr_list:
        if addr['ip'] in enable_ip:
            ip_and_ports.append(addr)

    print(ip_and_ports)

# dq.get_peers(info_hash=b'T\x86\x12W\xc3\xefj\x01x\xd2\x984`\nN\xf1\xe1\xc6!@')
