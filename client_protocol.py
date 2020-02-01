import asyncio
import logging


class DHTClientProtocol(asyncio.DatagramProtocol):
    def __init__(self, data, loop, timeout=1):
        self.data = data
        self.loop = loop
        self.transport = None
        self.timeout = timeout
        self.response = None
        self.connection_end = loop.create_future()

    def connection_made(self, transport):
        self.transport = transport
        logging.info("Connection made")
        self.transport.sendto(self.data)  # data is bencoded

        # logging.info(f"Timer {self.timeout} sec")
        self.timer()

    def datagram_received(self, data, addr):
        logging.info(f"Received: {data}")
        self.response = data
        self.transport.close()

    def error_received(self, e):
        logging.error(f"Exception Occured : {e}")
        self.stop_timer()
        self.transport.close()

    def connection_lost(self, e):
        logging.info("Connection closed")
        self.stop_timer()
        if not self.connection_end.done():
            # self.connection_end.set_result(True)
            self.connection_end.set_result(self.response)

    def timer(self):
        self.timer = self.loop.call_later(self.timeout, self.timeout_handler)

    def stop_timer(self):
        if self.timer:
            self.timer.cancel()

    def timeout_handler(self):
        logging.error("Error : Connection Timeout")
        self.transport.close()
        self.connection_end.set_result(False)


async def client(data, *target_addr):
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: DHTClientProtocol(data, loop),
        remote_addr=target_addr
    )  # ("127.0.0.1", 40000)
    try:
        await protocol.connection_end
    finally:
        transport.close()


if __name__ == '__main__':
    asyncio.run(client())
