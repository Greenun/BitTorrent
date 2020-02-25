from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.sql import select, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import InvalidRequestError
from .models import Base, ValidNodes, TargetNodes, TorrentInfo
from ..utils.tools import get_distance
import heapq

# for memo
# https://docs.sqlalchemy.org/en/13/orm/query.html
# https://itnext.io/sqlalchemy-orm-connecting-to-postgresql-from-scratch-create-fetch-update-and-delete-a86bc81333dc

# need to be env
ROOT = 'postgres'
PASSWORD = '0584qwqw'
PORT = 5432
DB_NAME = 'dht_database'


def manage_session(task):
    def session_task(self, *args, **kwargs):
        session = sessionmaker(self.engine)()
        result = task(self, session, *args, **kwargs)
        session.close()
        # return result
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
    def select_all_valid(self, session):
        # select
        records = session.query(ValidNodes).all()
        return records

    @manage_session
    def select_all_target(self, session):
        records = session.query(TargetNodes).all()
        return records

    @manage_session
    def select_all_info(self, session):
        records = session.query(TorrentInfo).all()
        return records

    @manage_session
    def select_close_targets(self, session, node_id):
        records = session.query(TargetNodes).limit(64) # 임시
        distances = list()
        for target_node in records:
            distance = get_distance(node_id, target_node.node_id)
            node_info = {
                'node_id': target_node.node_id,
                'ip': target_node.ip,
                'port': target_node.port,
            }
            heapq.heappush(distances, (distance, node_info))
        ret = list()
        for i in range(8):
            ret.append(heapq.heappop(distances))
        return ret

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
