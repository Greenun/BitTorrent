from sqlalchemy import create_engine
from sqlalchemy.sql import select, text
from sqlalchemy.orm import sessionmaker
from models import Base


#for memo
ROOT = 'postgres'
PASSWORD = '0584qwqw'
PORT = 5432
DB_NAME = 'dht_database'

#session
def manage_session(task):
	def session_task(self, *args, **kwargs):
		session = sessionmaker(self.engine)()
		result = task(self, session, *args, **kwargs)
		session.close()
		#return True
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
			+ "@"+ host + ":" 
			+ str(port) + "/" + db_name,
			echo = debug
		)
		#self.session = sessionmaker(self.engine)()

		Base.metadata.create_all(self.engine)

	def create_database(self, user, password, db_name, host='localhost', port=5432):
	#create database if not exist
		engine = create_engine("postgresql://" + user
			+ ":" + password
			+ "@"+ host + ":" 
			+ str(port) + "/" + "postgres",
			echo = True
		)

		conn = engine.connect()
		db_name_query = select([text("datname")]).select_from(text("pg_database"))
		result = conn.execute(db_name_query)

		if not (self.db_name,) in result.fetchall():
			conn.execute("commit")#end current transaction block
			conn.execute("create database "+self.db_name)
			conn.execute("commit")
		conn.close()
		engine.dispose()

		return True

	#create table with metadata
	def create_table(self):
		pass

	#insert
	@manage_session
	def insert(self, session, data):
		#data --> object to insert
		print('insert')

	#select
	@manage_session
	def select(self, session, data):
		pass

	@manage_session
	def update(self, session, data):
		pass

	@manage_session
	def delete(self, session, data):
		pass

if __name__ == "__main__":
	#from sqlalchemy.sql import exists, select, text
	#create_database(ROOT, PASSWORD, "dht_database")
	ddb = DHTDatabase(ROOT, PASSWORD, DB_NAME, debug=True)
	ddb.insert('test')
	'''eg = create_engine('postgresql://'+ROOT+":"+PASSWORD+"@localhost:"+str(PORT)+"/"+"postgres", echo=True)
	conn = eg.connect()
	#conn.execute("commit")
	t = select([text("datname")]).select_from(text("pg_database"))
	
	result = conn.execute(t)
	print(dir(result))
	print(result.context)
	#print(result.fetchall())

	#for i in result:
	#	print(i)
	if ('wiki',) in result.fetchall():
		print("good")
	print(result.next())
	conn.execute("commit")
	conn.close()
	#print(eg)
	'''
