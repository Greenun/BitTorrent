import asyncio

class BitClientProtocol(asyncio.DatagramProtocol):
	def __init__(self, data, loop, timeout=1):
		self.data = data
		self.loop = loop
		self.transport = None
		self.timeout = timeout
		self.connection_end = loop.create_future()

	def connection_made(self, transport):
		self.transport = transport
		print("Connection Made")
		#if not isinstance(self.data, str): self.data = str(self.data)
		#self.transport.sendto(self.data.encode())
		self.transport.sendto(self.data)#data is bencoded

		print("timer start")
		self.timer()

	def datagram_received(self, data, addr):
		print("Received: ", data)#.decode()
		self.transport.close()

	def error_received(self, e):
		print("Exception Occured : ", e)
		self.stop_timer()
		self.transport.close()

	def connection_lost(self, e):
		print("Connection closed")
		self.stop_timer()
		if not self.connection_end.done():
			self.connection_end.set_result(True)

	def timer(self):
		self.timer = self.loop.call_later(self.timeout, self.timeout_handler)

	def stop_timer(self):
		if self.timer:
			self.timer.cancel()

	def timeout_handler(self):
		print("Error : Connection Timeout")
		self.transport.close()
		self.connection_end.set_result(False)


async def client(data, *target_addr):
	#client(ip, port) --> (ip, port)
	loop = asyncio.get_running_loop()

	transport, protocol = await loop.create_datagram_endpoint(
		lambda: BitClientProtocol(data, loop),
		remote_addr=target_addr
	)#("127.0.0.1", 40000)
	try:
		await protocol.connection_end
	finally:
		transport.close()

if __name__ == '__main__':
	asyncio.run(client())