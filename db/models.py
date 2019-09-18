from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
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

'''class TargetNodes(Base):
	__tablename__ = 'target_nodes'

	id = Column(Integer, primary_key=True)
	node_id = Column(String, nullable=False, unique=True)
	ip = Column(String, nullable=False)
	port = Column(Integer, nullable=False)
	good_node = Column(Boolean, default=False)
	created_time = Column(DateTime, default=datetime.datetime.utcnow)
	#valid node as foreing key --> close node list'''
		