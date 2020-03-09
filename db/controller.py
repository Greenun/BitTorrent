from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, text
from sqlalchemy.sql.expression import func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
from BitTorrent.db.models import Base, ValidNodes, TargetNodes, TorrentInfo
from BitTorrent.utils.tools import get_distance
from BitTorrent.utils.heap import DistanceHeap, Node

# for memo
# https://docs.sqlalchemy.org/en/13/orm/query.html
# https://itnext.io/sqlalchemy-orm-connecting-to-postgresql-from-scratch-create-fetch-update-and-delete-a86bc81333dc

# need to be env
ROOT = 'postgres'
PASSWORD = '0584qwqw'
PORT = 5432
DB_NAME = 'dht_database'


def get_random(records):
    import random
    if records.count() == 0:
        return None
    idx = random.randint(0, records.count() - 1)
    return records[idx]


def manage_session(task):
    def session_task(self, *args, **kwargs):
        session = sessionmaker(self.engine)()
        result = task(self, session, *args, **kwargs)
        session.close()
        return result
    return session_task


class DHTDatabase(object):
    def __init__(self, user, password, db_name, host='localhost', port=5432, debug=False):
        self.user = user
        self.password = password
        self.db_name = db_name
        self.host = host
        self.port = port

        self.engine = create_engine("postgresql://" + user
                                    + ":" + password
                                    + "@" + host + ":"
                                    + str(port) + "/" + db_name,
                                    echo=debug
                                    )

    def create_database(self, host='localhost', port=5432):
        # create database if not exist
        engine = create_engine("postgresql://" + self.user
                               + ":" + self.password
                               + "@" + host + ":"
                               + str(port) + "/" + "postgres",
                               echo=True
                               )

        conn = engine.connect()
        db_name_query = select([text("datname")]).select_from(text("pg_database"))
        result = conn.execute(db_name_query)

        if not (self.db_name,) in result.fetchall():
            conn.execute("commit")  # end current transaction block
            conn.execute("create database " + self.db_name)
            conn.execute("commit")
        conn.close()
        engine.dispose()

        return True

    @manage_session
    def insert(self, session, data):
        # insert
        # data --> model object to insert
        if isinstance(data, list):
            session.bulk_save_objects(data)
        else:
            session.add(data)
        try:
            session.commit()
        except InvalidRequestError:
            session.rollback()
            return False
        return True

    @manage_session
    def select_random_valid(self, session):
        # select
        records = session.query(ValidNodes).order_by(func.random()).limit(32)
        return records

    @manage_session
    def select_all_target(self, session):
        records = session.query(TargetNodes).all()
        return records

    @manage_session
    def select_random_info(self, session):
        records = session.query(TorrentInfo).order_by(func.random()).limit(64)
        return records

    @manage_session
    def select_close_targets(self, session, node_id):
        records = session.query(TargetNodes).order_by(func.random()).limit(64)
        distances = DistanceHeap()
        for target_node in records:
            distance = get_distance(node_id, target_node.node_id)
            node_info = {
                'node_id': target_node.node_id,
                'ip': target_node.ip,
                'port': target_node.port,
            }
            distances.push(Node(distance, node_info))
        ret = list()
        import copy
        for i in range(8):
            ret.append(copy.deepcopy(distances.pop().node_info))
        # print(ret)
        return ret

    @manage_session
    def select_random_nodes(self, session, limit=8):
        records = session.query(TargetNodes).order_by(func.random()).limit(8)
        target_nodes = list()
        for record in records:
            target_nodes.append(record)
        print(target_nodes)
        return target_nodes

    @manage_session
    def select_target(self, session, node_id):
        records = session.query(TargetNodes).filter_by(node_id=node_id).all()
        print(node_id, records)
        if records:
            return records[0]
        return None

    @manage_session
    def update(self, session, data):
        pass

    @manage_session
    def delete(self, session, data):
        pass


if __name__ == "__main__":
    # ddb = DHTDatabase(ROOT, PASSWORD, DB_NAME, debug=True)
    # create model metadata
    engine = create_engine("postgresql://" + ROOT
        + ":" + PASSWORD
        + "@" + 'localhost' + ":"
        + str(5432) + "/" + DB_NAME,
        echo=True
    )
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
