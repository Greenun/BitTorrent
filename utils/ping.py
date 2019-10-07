import socket
import struct
import select
import sys

class Ping(object):
	def __init__(self, etime=0.5):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, 1)
		self.socket.settimeout(etime)
		self.packet = None
		self.sockets = None

	def make_packet(self, data="A"):
		_type = 8#echo
		_code = 0#no code in echo
		_checksum = 0
		_etc = 1
		header = struct.pack("!bbHI", _type, _code, _checksum, _etc)#, _seq
		_checksum = self.calculate_chksum(header)
		#print(_checksum)
		header = struct.pack("!bbHI", _type, _code, _checksum, _etc)
		self.packet = header
		return header

	def calculate_chksum(self, data):
		_sum = 0
		size = len(data)
		if (size % 2) == 1:
			data += b'\x00'
			size += 1
		for i in range(0, size, 2):
			_sum += data[i]*256 + data[i+1]

		while not ((_sum >> 16) == 0):
			_sum = (_sum >> 16) + (_sum & 0xFFFF)
		_sum = ~_sum & 0xFFFF
		return _sum

	def send(self, ip_list, data=None):
		if not self.packet:
			self.make_packet()
		for ip in ip_list:
			self.socket.sendto(self.packet, (ip, 0))

	def multi_send(self, ip_list, data=None):
		if not self.packet:
			self.make_packet()

		sockets = []
		for ip in ip_list:
			info = {"ip": ip,
					"socket": socket.socket(socket.AF_INET, socket.SOCK_RAW, 1),
				}
			sockets.append(info)
		for s in sockets:
			s["socket"].sendto(self.packet, (s["ip"], 0))
		self.sockets = sockets
		#for i in self.sockets:
		#	print(i["socket"].getblocking())

	def receive(self, ip_list):
		#import time
		done_list = list()
		failed_count = 0
		
		if self.sockets:
			#rd, wr, _ = select.select([x["socket"] for x in self.sockets], [], [], 0.3)#0.3
			while 1:
				rd, wr, _ = select.select([x["socket"] for x in self.sockets], [], [], 0.3)#0.3
				if not rd: continue#break if no waiting
				for d in rd:
					try:
						print(d)
						recv, addr = d.recvfrom(1024)
						done_list.append(addr)
					except:
						failed_count += 1
						print(sys.exc_info())
		else:
			try:
				pass
			except:
				print(sys.exc_info())


		'''rd, wr, ex = select.select([self.socket]*len(ip_list), [], [], 0.3)
		#print(rd)
		print(len(rd))
		for s in rd:
			try:
				recv, addr = s.recvfrom(1024)
				done_list.append(addr)
			except socket.timeout:
				failed_count += 1
		'''

		'''while (len(done_list) + failed_count)  < len(ip_list):
			try:
				recv, addr = self.socket.recvfrom(1024)
				#print(recv)
				#print(addr)
				done_list.append(addr)
			except socket.timeout:
				failed_count += 1
		'''

		print("Ping failed : " + str(failed_count))
		return done_list

	def ping_check(self, ip_list):
		#self.send(ip_list)
		self.multi_send(ip_list)

		enable_ip = self.receive(ip_list)
		return enable_ip

if __name__ == '__main__':
	ip_list = ["8.8.8.8", "127.0.0.1"]
	p = Ping()
	p.ping_check(ip_list)