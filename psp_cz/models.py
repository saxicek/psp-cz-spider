# coding=utf-8
from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey, UniqueConstraint, Index
from database import Base

class Sitting(Base):
    __tablename__ = 'sitting'
    __table_args__ = (
                      Index('ix_sit_url', 'url'),
                      )

    id = Column(Integer, primary_key=True)
    url = Column(String(4000), unique=True)
    name = Column(String(255))

    votings = relationship('Voting', backref='sitting')

    def __init__(self, url=None, name=None):
        self.url = url
        self.name = name

    def __repr__(self):
        return '<Zasedání %r>' % (self.name)

    def values(self):
        """Used for JSON serializing. Must be a better way to do this. :-("""
        return dict(id      = self.id,
                    url     = self.url,
                    name    = self.name)

class Voting(Base):
    __tablename__ = 'voting'
    __table_args__ = (
                      Index('ix_vot_url', 'url'),
                      Index('ix_vot_sitting_id', 'sitting_id'),
                      Index('ix_vot_voting_date', 'voting_date')
                      )

    id = Column(Integer, primary_key=True)
    url = Column(String(4000), unique=True)
    voting_nr = Column(Integer)
    name = Column(String(500))
    voting_date = Column(Date)
    minutes_url = Column(String(4000))
    result = Column(String(50))
    sitting_id = Column(Integer, ForeignKey('sitting.id'))

    parlMembVotings = relationship('ParlMembVoting', backref='voting')
    votingReviews = relationship('VotingReview', backref='voting')

    def __init__(self, url=None, voting_nr=None, name=None, voting_date=None, minutes_url=None, result=None, sitting=None):
        self.url = url
        self.voting_nr = voting_nr
        self.name = name
        self.voting_date = voting_date
        self.minutes_url = minutes_url
        self.result = result
        self.sitting = sitting

    def __repr__(self):
        return '<Hlasování %r>' % (self.name)

    def values(self):
        """Used for JSON serializing. Must be a better way to do this. :-("""
        return dict(id          = self.id,
                    url         = self.url,
                    voting_nr   = self.voting_nr,
                    name        = self.name,
                    voting_date = self.voting_date.isoformat(),
                    minutes_url = self.minutes_url,
                    result      = self.result,
                    sitting_id  = self.sitting_id)

class ParlMemb(Base):
    __tablename__ = 'parl_memb'
    __table_args__ = (
                      Index('ix_pm_url', 'url'),
                      )

    id = Column(Integer, primary_key=True)
    url = Column(String(4000), unique=True)
    name = Column(String(255))

    parlMembVotings = relationship('ParlMembVoting', backref='parlMemb')

    def __init__(self, url=None, name=None):
        self.url = url
        self.name = name

    def __repr__(self):
        return '<Poslanec %r>' % (self.name)

    def values(self):
        """Used for JSON serializing. Must be a better way to do this. :-("""
        return dict(id   = self.id,
                    url  = self.url,
                    name = self.name)

class ParlMembVoting(Base):
    __tablename__ = 'parl_memb_voting'
    __table_args__ = (
                      UniqueConstraint('vote', 'parl_memb_id', 'voting_id'),
                      Index('ix_pmv_parl_memb_id', 'parl_memb_id'),
                      Index('ix_pmv_voting_id', 'voting_id'),
                      )

    id = Column(Integer, primary_key=True)
    vote = Column(String(1))
    parl_memb_id = Column(Integer, ForeignKey('parl_memb.id'))
    voting_id = Column(Integer, ForeignKey('voting.id'))

    def __init__(self, vote=None, parlMemb=None, voting=None):
        self.vote = vote
        self.parlMemb = parlMemb
        self.voting = voting

    def __repr__(self):
        return '<%r, %r - %r>' % (self.voting, self.parlMemb, self.vote)

    def values(self):
        """Used for JSON serializing. Must be a better way to do this. :-("""
        return dict(id           = self.id,
                    vote         = self.vote,
                    parl_memb_id = self.parl_memb_id,
                    voting_id    = self.voting_id)

class VotingReview(Base):
    __tablename__ = 'voting_review'

    id = Column(Integer, primary_key=True)
    title = Column(String(160))
    reasoning = Column(String)
    voting_id = Column(Integer, ForeignKey('voting.id'))

    def __init__(self, title=None, reasoning=None, voting=None):
        self.title = title
        self.reasoning = reasoning
        self.voting = voting

    def __repr__(self):
        return '<Komentář k hlasování - %r>' % (self.title)

    def values(self):
        """Used for JSON serializing. Must be a better way to do this. :-("""
        return dict(id           = self.id,
                    title        = self.title,
                    reasoning    = self.reasoning,
                    voting_id    = self.voting_id)
