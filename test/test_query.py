import logging
import asyncio
from BitTorrent.query import DHTQuery
from BitTorrent.utils import clock
from BitTorrent.db import controller

c = clock.Clock()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


@c.clock_execute
def test_ping(dest):
    dq = DHTQuery()
    resp = asyncio.run(dq.async_ping(dest=dest))
    logging.info(resp)


@c.clock_execute
def test_find_node():
    dq = DHTQuery()
    # node_id=b'\x85\xc5\xdf\x7f\x7fri\xb51\x12\x85\xd2\xb5\xd7\x0c\xca\xdd5HU'

    resp = asyncio.run(dq.async_find_node(
        dest=("178.164.195.83", 27860),
        target=b'\x9f\x3a\x9e\xe9\x8a\x0f\x87\x18\xe8\x67\x66\x1d\x88\x25\xbd\x3e\xe0\xa4\x3e\x83'
    ))
    logging.info(resp)


@c.clock_execute
def test_get_peers():
    dq = DHTQuery(info_hash=b'T\x86\x12W\xc3\xefj\x01x\xd2\x984`\nN\xf1\xe1\xc6!@')
    resp = dq.get_peers(
        dest=("178.164.195.83", 27860),
    )
    logging.info(resp)


@c.clock_execute
def test_collect_nodes():
    ctl = controller.DHTDatabase(
        user="wessup",
        password="0584qwqw",
        db_name="dht_database",
    )
    node_id = controller.get_random(ctl.select_random_valid())
    info_hash = controller.get_random(ctl.select_random_info())
    dq = DHTQuery(
        node_id=node_id,
        info_hash=info_hash,
        controller=ctl
    )
    healthy = dq.collect_nodes()
    logging.info(healthy)


@c.clock_execute
def test_spread_nodes():
    ctl = controller.DHTDatabase(
        user="wessup",
        password="0584qwqw",
        db_name="dht_database",
    )
    # z = ctl.select_all_target()[0]
    # print(z)
    #
    # x = ctl.select_target(b'\x83\xbf\x9d\xb1\xe9\xe3\x7e\x55\x50\x8f\x86\xe6\x41\xa8\xbe\x5e\xf4\xff\x34\xca')
    # print(x)
    node_id = controller.get_random(ctl.select_random_valid())
    info_hash = controller.get_random(ctl.select_random_info())

    dq = DHTQuery(
        node_id=node_id,
        info_hash=info_hash.info_hash,
        controller=ctl
    )
    success, nodes = dq.spread_nodes(random=False)
    if success:
        logging.info(nodes)
    logging.info("spread nodes end.")


# transaction id 는 repsonse , request 동일
if __name__ == '__main__':
    # test_find_node()
    # test_get_peers()
    # test_collect_nodes()
    # test_ping(('174.3.136.144', 50321))
    test_spread_nodes()
