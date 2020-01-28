from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects import postgresql
import datetime

Base = declarative_base()


class ValidNodes(Base):
	__tablename__ = 'valid_nodes'

	id = Column(Integer, primary_key=True)
	node_id = Column(String, nullable=False, unique=True)
	using = Column(Boolean, default=False)
	created_time = Column(DateTime, default=datetime.datetime.utcnow)
	#target node as foreing key

	def __repr__(self):
		return f"<ValidNodes(id={self.id}, node_id={self.node_id}, using={self.using}, created_time={self.created_time})>"


# 응답하는 노드 저장
class TargetNodes(Base):
	__tablename__ = 'target_nodes'

	id = Column(Integer, primary_key=True)
	node_id = Column(String, nullable=False, unique=True)
	ip = Column(postgresql.INET, nullable=False)
	port = Column(Integer, nullable=False)
	created_time = Column(DateTime, default=datetime.datetime.utcnow)


# 사용 가능한 info hash 저장
class InfoHash(Base):
	pass
