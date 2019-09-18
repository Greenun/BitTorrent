import codecs
import sys
import uuid
import hashlib
import os
import codecs

NODES= ["5531578c820db4a4d0d9d47888c7754c477d1d01",
			"90cccc0b9b263d06698e31a06453c3c4879f088f",
			"1700db1dc2095c763699a68a33e4a6a7a9aa1f32",
			"150d31a02dd3efec378891618035931ff2b72c72"]
STATIC_PORT = 6881

'''
Random Generate Objects such as node_id, info_hash, transaction_id
'''
class RandomArgs(object):
	def __init__(self, nid=None, ih=None, tid=None):
		self.hf = hashlib.sha1()
		#self.ihf = hashlib.sha1()
		#self._transaction_id = self._generate_tid() if not tid else tid
		#self._node_id = self._generate_nid() if not nid else bytes.fromhex(nid)
		#self._info_hash = self._generate_ih() if not ih else ih
		self._generate_tid() if not tid else tid
		#self._generate_nid() if not nid else bytes.fromhex(nid)
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

		#format of hex string to hex bytes
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
		return self._transaction_id
	
	
#to bytes / to str
def convert(value, mode):
	if mode == 'b':
		return bytes.fromhex(value)
	elif mode == 's':
		return value.hex()
	else:
		print("Error: mode argument must be 'b' or 's'", file=sys.stderr)
		sys.exit(0)

#use for find_nodes 
def extract_nodes(nodes):
	node_list = [nodes[x:x+26] for x in range(0, len(nodes), 26)]#map("".join, zip(*[iter(nodes)]*2))
	print(node_list)
	info_dict = {}
	def extract_detail(value):
		assert isinstance(value, list)
		idx = 0
		for v in value:
			d = {}
			d['ip'] = '.'.join(['{}'.format(x) for x in v[20:24]])
			d['port'] = int.from_bytes(v[24:], 'big')
			d['nodeid'] = convert(v[0:20], 's')
			info_dict[str(idx)] = d
			idx += 1
		return info_dict
	return _nodes_to_list(extract_detail(node_list))

def _nodes_to_list(node_dict):
	#form : {'ip': blah, 'port': blah, 'nodeid': blahblah}

	node_list = list()
	for key in node_dict:
		node_list.append(node_dict[key])
	return node_list

def get_hash(filename):
	'''
		filename is based on --current-- root file directory
		/utils X -> /
	'''
	current_path = os.path.dirname(os.path.abspath(__file__))
	filepath = os.path.join(current_path, '../' ,filename)
	with codecs.open(filepath, 'rb') as f:
		from bencoder import bdecode
		content = bdecode(f.read())
		piece = content[b'info'][b'pieces']
	#sha = hashlib.sha1()
	#sha.update(piece)
	length = content[b'info'][b'length']
	piece_length = content[b'info'][b'piece length']
	print(piece[0:20])
	print(piece[0:20].hex())

	


def make_query(query, options=None):
	random_str = uuid.uuid4().hex
	random_tid = uuid.uuid4().hex[0:2]#transaction id
	sha = hashlib.sha1()

	sha.update(random_str.encode())
	random_node = bytes.fromhex(sha.hexdigest())
	argument = {"t": random_tid, "y": "q"}
	argument["q"] = query

	if query == 'ping':
		argument["a"] = {"id": NODES[0]}#임시
	elif query == 'find_node':
		#options : target node
		assert options
		argument["a"] = {"id": NODES[0], "target": options}#임시
	elif query == 'get_peers':
		#options : info hash
		if not options:			
			sha.update(uuid.uuid4().hex)
			random_info = bytes.fromhex(sha.hexdigest())
			argument["a"] = {"id": NODES[0], "info_hash": random_info}#임시
		else:
			argument["a"] = {"id": NODES[0], "info_hash": options}#임시
	elif query == 'announce_peer':
		#options : info hash, token(from get_peers) tuple(ih, to)
		assert isinstance(options, tuple) or isinstance(options, list)
		argument["a"] = {"id": NODES[0], "implied_port": 0,  "info_hash": options[0], "port": STATIC_PORT, "token": options[1]}#임시

	return argument

if __name__ == '__main__':
	#x = extract_nodes(b'J\x12\xaf\x08\xf2\x89\xab\xc9\x9f2\xcc\xdb\xbe\x89\x9a\xb3|u\x8f\x8aV<\xd5!6\x94(\xf2b0T\xbe/E\x1a\xe0\xcf\x08\xd1\xa3\xe2\xdc\x82+\xfdlzn\x7fI\xf3\x8cM\xe9\xb0\x17\xea\x1a|\x82\xe7t[s\xd7\xffj\x0e-B\x7f\x1a\xbcTe\xf2\x1a\xe1\x10/!\xc3r\x114\x1dS"<\x1b\xeb*\x11\x93\x8b\x7f\xe1\xe1]uO\xcc\xdbu\xa1\n\xb4W~`G~\x87\x98\xa8N\x9f\xdb!\xfbs\xc8\xaersI\xd8\xc0\xad\xba\xffU\xa5\xebQT\xf0gJ`\xc3\x9c\xb5*l#%\x8a\nO\x02\xda\xec^\xc4\x91QB\xf3V\xf4\xa6\t\x997\xcfB\x9a2\x13\xe5\xe6\x1c\xfc\x8e\xdfOk\xcdf\x17\x80\xa3B:5\x1f\x16K.\xdd/(N\xb3\xd2\x9cF\x91J\x86\xf7_%\xa0\xe0\xa9K5(@Era7\x9bw\x81\xf1\\\xa4\xb6ap\xd2\x1b\x0f/y\xd3\x16\xf5\x1a\xe1M\xb4\xd2md\x7f\xe7\xae}P\xf8\x13\x8c\xdb\xbb\xbe\xbe\x1a\x14t\xc8\xbd\x08\xaa\x9b?\x06qA\x8c\xab\xbf\xdeZ\x87\x91u\xb0{\x15\x0c\xc4\xf4\xd2\x9c\x00\xd5\x7fe\x87\xd1t\x9fU\x15_e\xf6\x06{]g\xe5\x8d`\xf3\xc7\x95~4p\xb2P\xf8NR`\xd0;k^\x14N\xa8O`!I\x14z\xb9\xd9\x10-<Wl\x18\xdb[\xb7]\xa5\xaa\xbd.\xba\xd4\x04p\\]\xady\\\x8c\x1e\x86V\xb3\xf3nM\xf8\x05\xa6\xf44^/w\x84_\xec\xbd\xdb\xf0\x9a\xd7?q\xf0H9\xdb(\r \x07"\x97\xe02\xf1\x8b\x90\xe2k\xfft&/[\xb8x\x86"\x9a\x05\x9c\xfe\xf0\xa8\xf7\xaa\xd0c\x07\x95\x9f]\xaf')
	#print(x)
	get_hash("ubuntu-18.04.3-live-server-amd64.iso.torrent")
	#print(x)