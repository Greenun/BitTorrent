import asyncio
from asyncio import transports
import logging
from .utils import bencoder
from .db.models import TargetNodes
from .db.controller import DHTDatabase


class DHTServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, loop, controller: DHTDatabase):
        logging.getLogger().setLevel(logging.INFO)
        self.loop = loop
        self.controller = controller

    def connection_made(self, transport: transports.BaseTransport) -> None:
        logging.info(f"Client Connected: {transport.get_extra_info('peername')}")

    def datagram_received(self, data, addr: (str, int)) -> None:
        logging.info(f"Data From {addr}")
        decoded = bencoder.bdecode(data)
        logging.info(f"Contents: {decoded}")
        # self.conroller.query()

    def error_received(self, exc: Exception) -> None:
        pass

    def connection_lost(self, exc) -> None:
        pass

