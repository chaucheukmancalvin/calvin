from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
 
engine = create_engine('sqlite:///205.db', echo=True)
Base = declarative_base()
 
########################################################################

class User(Base):

    __tablename__ = "user"

    username = Column(String, primary_key=True)
    password = Column(String)
    email = Column(String)
    creditcardNo = Column(Integer)
    
    

class Sell(Base):

    __tablename__ = "sell"
    
    id = Column(Integer, primary_key=True)
    detail = Column(String)
    price = Column(Integer)
    username = Column(String, ForeignKey("user.username"))
    modle = Column(String)
    state = Column(String)
    date = Column(Date)

class Admin(Base):
    
    __tablename__ = "admin"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)

class Product(Base):

    __tablename__ = "product"
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey("user.username"))
    purchaseno = Column(Integer) 
    modle = Column(String)


class Component(Base):

    __tablename__ = "component"
    id = Column(Integer, primary_key=True)
    username = Column(String, ForeignKey("user.username"))
    Purchaseno = Column(Integer) 
    modle = Column(String)

def __init__(self, username, password, creditcardNo, detail, price, modle, state, date, purchaseno, Purchaseno, email):
    
    self.username = username
    self.password = password
    self.creditcardNo = creditcardNo
    self.detail = detail
    self.price = price
    self.modle = modle
    self.state = state
    self.date = date
    self.purchaseno = purchaseno
    self.Purchaseno = Purchaseno
    self.email = email

# create tables
Base.metadata.create_all(engine)
