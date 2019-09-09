import re
#integer : i<contents>e e.g., i42e
#byte string : length:contents e.g., 4:spam
#list : l<contents>e e.g., [spam, 42] = l4:spami42ee
#dictionary : d<contents>e  e.g., {"bar": "spam", "foo": 42} = d3:bar4:spam3:fooi42ee

def ordering_keys(target_dict):
	target_keys = list(target_dict.keys())
	target_keys.sort()
	return target_keys

#return string
def bencode(value):
	#assert isinstance(value, dict)
	encoded = b""
	if isinstance(value, dict):
		target_keys = ordering_keys(value)
		encoded += b"d"
		for target_key in target_keys:
			target_value = value[target_key]
			encoded += bencode(target_key)
			encoded += bencode(target_value)
		encoded += b"e"
	elif isinstance(value, list):
		encoded += b"l"
		encoded += b"".join(map(value, bencode))
		encoded += b"e"
	elif isinstance(value, str):
		encoded += str(len(value)).encode() + b":" + value.encode()
	elif isinstance(value, int):
		encoded += b"i" + str(value).encode() + b"e"
	elif isinstance(value, bytes):
		encoded += str(len(value)).encode() + b":" + value
	else:
		pass
	return encoded


def bdecode(value):
	assert isinstance(value, bytes)
	def decode_sequence(value):
		if value.startswith(b'd') or value.startswith(b'l'):
			ret_list = []
			rem = value[1:]
			#print(rem)
			while not rem.startswith(b'e'):
				ret, rem = decode_sequence(rem)
				ret_list.append(ret)
				#print(ret_list)
				#print(rem)
			rem = rem[1:]
			if value.startswith(b'd'):
				return {k:v for k,v in zip(ret_list[::2], ret_list[1::2])}, rem
			else:
				return ret_list, rem
		elif value.startswith(b'i'):
			rem = value[1:]
			search = re.search(rb'e', rem)
			decoded = int(value[1:search.end()])
			return decoded, value[search.end()+1:]
		elif re.search(rb'\d:', value):
			search = re.search(rb'(\d+):', value)
			length = int(search.group(1))
			decoded = value[search.end():search.end()+length]
			return decoded, value[search.end()+length:]
		else:
			pass
	ret, blank = decode_sequence(value)
	return ret

if __name__ == '__main__':
	x = {"t":"aa", "y":"q", "q":"find_node", "a": {"id":"abcdefghij0123456789", "target":"mnopqrstuvwxyz123456"}}#{"t":"aa", "y":"e", "e":[201, "A Generic Error Ocurred"]}
	answer = b"d1:ad2:id20:abcdefghij01234567896:target20:mnopqrstuvwxyz123456e1:q9:find_node1:t2:aa1:y1:qe"#"d1:eli201e23:A Generic Error Ocurrede1:t2:aa1:y1:ee"
	t = bencode(x)
	print(answer == t)
	print(t)
	q= bdecode(t)
	print(q)
	print(type(q))