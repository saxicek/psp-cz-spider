# coding=utf-8
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey, UniqueConstraint
from database import Base

class Sitting(Base):
    __tablename__ = 'sitting'
    id = Column(Integer, primary_key=True)
    url = Column(String(4000), unique=True, index=True)
    name = Column(String(255))

    votings = relationship('Voting', backref='sitting')

    def __init__(self, url=None, name=None):
        self.url = url
        self.name = name

    def __repr__(self):
        return '<Zasedání %r>' % (self.name)

class Voting(Base):
    __tablename__ = 'voting'
    id = Column(Integer, primary_key=True)
    url = Column(String(4000), unique=True, index=True)
    name = Column(String(255))
    sitting_id = Column(Integer, ForeignKey('sitting.id'), index=True)

    parlMembVotings = relationship('ParlMembVoting', backref='voting')

    def __init__(self, url=None, name=None, sitting=None):
        self.url = url
        self.name = name
        self.sitting = sitting

    def __repr__(self):
        return '<Hlasování %r>' % (self.name)

class ParlMemb(Base):
    __tablename__ = 'parl_memb'
    id = Column(Integer, primary_key=True)
    url = Column(String(4000), unique=True, index=True)
    name = Column(String(255))

    parlMembVotings = relationship('ParlMembVoting', backref='parlMemb')

    def __init__(self, url=None, name=None):
        self.url = url
        self.name = name

    def __repr__(self):
        return '<Poslanec %r>' % (self.name)

class ParlMembVoting(Base):
    __tablename__ = 'parl_memb_voting'
    __table_args__ = (
                      UniqueConstraint('vote', 'parl_memb_id', 'voting_id'),
                      )
    id = Column(Integer, primary_key=True)
    vote = Column(String(1))
    parl_memb_id = Column(Integer, ForeignKey('parl_memb.id'), index=True)
    voting_id = Column(Integer, ForeignKey('voting.id'), index=True)

    def __init__(self, vote=None, parlMemb=None, voting=None):
        self.vote = vote
        self.parlMemb = parlMemb
        self.voting = voting

    def __repr__(self):
        return '<%r, %r - %r>' % (self.voting, self.parlMemb, self.vote)
 