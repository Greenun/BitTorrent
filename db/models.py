from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship, backref
import datetime

Base = declarative_base()


class ValidNodes(Base):
    __tablename__ = 'valid_nodes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(postgresql.BYTEA, nullable=False, unique=True)
    created_time = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<ValidNodes(id={self.id}, node_id={self.node_id}, using={self.using}, " \
               f"created_time={self.created_time})>"


class TargetNodes(Base):
    # responded nodes: icmp ping and bt ping
    __tablename__ = 'target_nodes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    node_id = Column(postgresql.BYTEA, nullable=False, unique=True)
    ip = Column(postgresql.INET, nullable=False)
    port = Column(Integer, nullable=False)
    created_time = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<TargetNodes(id={self.id}, node_id={self.node_id}, ip={self.ip}, port={self.port}, " \
               f"created_time={self.created_time}>"


class TorrentInfo(Base):
    # 사용 가능한 info hash 저장
    __tablename__ = 'torrent_info'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    info_hash = Column(postgresql.BYTEA, nullable=False)
    created_time = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<TorrentInfo(id={self.id}, name={self.name}, info_hash={self.info_hash}, " \
               f"created_time={self.created_time}>"


class AnnouncedNodes(Base):
    # announced nodes
    __tablename__ = 'announced_nodes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    announced = Column(Integer, ForeignKey('target_nodes.id'))
    target = relationship("TargetNodes", backref=backref("announced_id", order_by=id))
    created_time = Column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f"<{self.__class__.qualname__}(id={self.id}, announced={self.announced}, " \
               f"created_time={self.created_time})>"
