import asyncio
from .query import DHTQuery
from . import server_protocol
import logging


class DHTServer(object):
	def __init__(self):
		self.logger = logging.getLogger(self.__class__.__qualname__)
		self.loop = asyncio.get_event_loop()

	def run(self, port=6881):
		endpoint = self.loop.create_datagram_endpoint(
			lambda: server_protocol.DHTServerProtocol(self.loop, 'test', None),
			local_addr=("0.0.0.0", port)
		)

		transport, protocol = self.loop.run_until_complete(endpoint)
		try:
			self.loop.run_forever()
		except KeyboardInterrupt:
			logging.info("Close Server...")
		finally:
			transport.close()
			self.loop.close()

	def stop(self):
		pass


def runserver(port=None):
	server = DHTServer()
	server.run()


if __name__ == '__main__':
	runserver()