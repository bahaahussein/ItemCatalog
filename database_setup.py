from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Category(Base):
	__tablename__ = 'category'
	
	id = Column(Integer, primary_key=True)
	name = Column(String, nullable=False)
	
	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'id': self.id,
			'name': self.name
		}
		
		
class Item(Base):
	__tablename__ = 'item'
	
	name = Column(String, nullable=False)
	id = Column(Integer, primary_key=True)
	description = Column(String, nullable=False)
	category_id = Column(Integer, ForeignKey('category.id'))
	category = relationship(Category)
	
	@property
	def serialize(self):
		"""Return object data in easily serializeable format"""
		return {
			'cat_id' : self.category_id,
			'description' : self.description,
			'id': self.id,
			'title': self.name
		}
		
engine = create_engine('sqlite:///categoryitems.db')


Base.metadata.create_all(engine)