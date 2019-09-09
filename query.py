import asyncio
from utils.bencoder import *
from utils.tools import RandomArgs
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
	def __init__(self, node_id = None, info_hash = None):
		self.payload = dict()
		self.random = None
		if node_id and info_hash:
			self.random = RandomArgs(node_id, info_hash)
		elif node_id or info_hash:
			self.random = RandomArgs(node_id) if node_id else RandomArgs(None, info_hash)
		else:
			self.random = RandomArgs()
		
		self.protocol = BitClientProtocol

	def ping(self, target=(DHT_ROUTER, DHT_PORT)):
		arg_dict = {"id": self.random.node_id}

		self.prepare_payload("ping", arg_dict)

		print(self.payload)
		asyncio.run(self.send(target))

	def find_node(self, target):
		arg_dict = {
			"id": self.random.node_id,
			"target": None,
		}
		
		self.prepare_payload("find_node", arg_dict)

	def get_peers(self, info_hash, target):
		pass

	def announce_peer(self, info_hash, target):
		pass

	def prepare_payload(self, request_type, args):
		self.random._generate_tid()

		self.payload["t"] = self.random.transaction_id
		self.payload["y"] = "q"#class only for query
		self.payload["q"] = request_type
		self.payload["a"] = args

		print(self.payload)

		self.payload = bencode(self.payload)

	async def send(self, target_addr):
		assert isinstance(target_addr, tuple)
		loop = asyncio.get_running_loop()

		transport, protocol = await loop.create_datagram_endpoint(
			lambda: self.protocol(self.payload, loop),
			remote_addr = target_addr
		)

		try:
			await protocol.connection_end
			#how to know timeout occured
			
			if not protocol.connection_end.result():
				#can take error msg or return error
				pass
		except:
			transport.close()

if __name__ == "__main__":
	dq = DHTQuery()
	dq.ping()
