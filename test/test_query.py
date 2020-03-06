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
# b'd2:ip6::\x92\xd4\x03\xe6:1:rd2:id20:2\xf5NisQ\xffJ\xec)\xcd\xba\xab\xf2\xfb\xe3F|\xc2g5:nodes416:I\xbd,\x14\xecW\xf0:\x9d\xd3\x8fm\x0f\xa6\x02\xde\xe6\x04\xbc\x0e\xcaN\xefh\xe6\xe9\xe1\xd8@\x8d\xc9\x9c\xc1\xe3y\xb8\'\xc6\xd7\xcc\xa3o\xc7{WG\xb7\xb3\x1e\xc7+\x0bUhoZNV,\xe5mw\xfd\x9eL\x82\x90\x94Zb\x91M\x1f\r\xffI\xdeD\x0em\xd3\x9fP\xb71\xbd\x96*\xc7}U5\x90\xef%\x11\x8d\xdc.%R\xea+\x9b\x14\x05\xd6v\x98Y\x18\xcap\xe7\xa92\xb8\x19\xa5\xbc\xfbH\xf9\xce\xbe\x82\x0f\xb0\xb9\x810\xdf_\xdbiBSW\xb3\xdc T\xc3\x93\xd3\xf5z\xe9e\na`\x19\r\x1a\xe1 \x85.M]\xd3sh\x17\x8ew\x10Q:\xffW\xd5j\xfe\xfc\xb4\x96X\xdc\xc1\xe7f\xdaW\x06J\xe2\x91\xccM\x0c\x1c\xb0PZ\x8ezO\x88\xee\xd0M\xeaQ\x00\xce\xc5\x07Q\xacL\x80\xb19\x8c \x8b\xa0\x89\x10\xb894d\xc3\xd3\xd7j\xd0~\xfb\xfen\x10\xffvz[\xb5\x1c"X\xbc\x15\x1c5\x01\xae6H\xbf\x03f\xc9\xb4\xb0\xa0\x1a\xe1\xc2\xe4\xad\xfc7\xce\xcc\xeb\x18\x19\x87\rm\xa3\xd2\xc3&O%\xc7\xbe\x02\xedh\xe3\xf5\xb4c\xfd\xc7\xe9!a\xa3\xf3\xd2\xe2\xe4\xd2w\x92\xcaS\xbb\xe0h]\rt !\xad\xaa\x90\x85\xee\xd0\xd0\xe4T\x19%O\xe0\xa4\xbe \xa4W\xae:_m|\xdf\xce2\x00sv\xd4:\x8dT\xbc\xcd\xc4\x82\x98\xe7\xe8\x0b;\xbb\xaa\x87D\x1c\x18\xeeNE\x1a\xe1fu\x16\x11$\x99\x87\x8d6\xba5x@Uo\'\xfd\xe5\xf9\x13P\x04\xa7\xaa\xa2/\xcd\x025\x94\xf4\x9eo\x02\xe7K\x17=\xd9\xcd\xcc\xac%`\xea\x94Vd\x80\xc5\xc6\xfee1:t2:6e1:y1:re'
if __name__ == '__main__':
    # test_find_node()
    # test_get_peers()
    # test_collect_nodes()
    # test_ping(('174.3.136.144', 50321))
    test_spread_nodes()
