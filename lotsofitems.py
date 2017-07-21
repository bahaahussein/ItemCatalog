from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
 
from database_setup import Category, Base, Item
 
engine = create_engine('sqlite:///categoryitems.db')
Base.metadata.bind = engine
 
DBSession = sessionmaker(bind=engine)
session = DBSession()

soccer = Category(name='Soccer')
session.add(soccer)
session.commit()

baseball = Category(name='Baseball')
session.add(baseball)
session.commit()

hockey = Category(name='Hockey')
session.add(hockey)
session.commit()

snowboarding = Category(name='Snowboarding')
session.add(snowboarding)
session.commit()

frisbee = Category(name='Frisbee')
session.add(frisbee)
session.commit()

basketball = Category(name='Basketball')
session.add(basketball)
session.commit()

baseball = Category(name='Baseball')
session.add(baseball)
session.commit()

rock_climbing = Category(name='Rock Climbing')
session.add(rock_climbing)
session.commit()

skating = Category(name='Skating')
session.add(skating)
session.commit()

foosball = Category(name='Foosball')
session.add(foosball)
session.commit()

stick = Item(name='Stick', description='stick for hockey', category=hockey )
session.add(stick)
session.commit()

goggles = Item(name='Goggles', description='goggles for snowboarding', category=snowboarding )
session.add(goggles)
session.commit()

snowboard = Item(name='Snowboard', description='snowboard for snowboarding', category=snowboarding )
session.add(snowboard)
session.commit()

shinguards = Item(name='Two shinguards', description='shninguards to protect legs', category=soccer )
session.add(shinguards)
session.commit()

frisbeee = Item(name='Frisbee', description='frisbee for frisbee', category=frisbee )
session.add(frisbeee)
session.commit()

jersey = Item(name='Jersey', description='jersey to wear', category=soccer )
session.add(jersey)
session.commit()

cleats = Item(name='Soccer Cleats', description='cleats for soccer', category=soccer )
session.add(cleats)
session.commit()

print 'added succesfully'