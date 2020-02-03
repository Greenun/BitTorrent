import asyncio
from asyncio import transports
import logging
from .utils import bencoder
from .utils.tools import get_distance
from .db.models import TargetNodes
from .db.controller import DHTDatabase

PAGE_SIZE = 32

# for memo
# asyncio udp protocol (proxy)
# https://gist.github.com/vxgmichel/b2cf8536363275e735c231caef35a5df


class DHTServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, loop, server_id, controller: DHTDatabase):
        logging.getLogger().setLevel(logging.INFO)
        self.loop = loop
        self.server_id = server_id
        self.controller = controller
        self.transport = None

        # self.connection_end = loop.create_future()

    def connection_made(self, transport: transports.BaseTransport) -> None:
        self.transport = transport
        logging.info(f"Client Connected: {self.transport.get_extra_info('peername')}")

    def datagram_received(self, data, addr: (str, int)) -> None:
        logging.info(f"Data From {addr}")
        decoded = bencoder.bdecode(data)
        logging.info(f"Contents: {decoded}")
        target_nodes = self.conroller.query(TargetNodes).limit(PAGE_SIZE)
        distances = map(get_distance, [self.server_id for _ in range(PAGE_SIZE)], target_nodes)
        sorted_distances = sorted(distances)
        # response --> bencoded serialized data
        response = sorted_distances

        self.transport.sendto(response)

    def error_received(self, exc: Exception) -> None:
        pass

    def connection_lost(self, exc) -> None:
        pass

