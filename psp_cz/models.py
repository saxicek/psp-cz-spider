# coding=utf-8
from sqlalchemy import func, Column, Integer, String, Date, BigInteger, DateTime
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
    name_full = Column(String(255))
    born = Column(Date)
    picture_hash = Column(String(40)) # using SHA1 hash as picture identifier
    gender = Column(String(1))
    region_id = Column(Integer, ForeignKey('region.id'))
    polit_group_id = Column(Integer, ForeignKey('polit_group.id'))

    parlMembVotings = relationship('ParlMembVoting', backref='parlMemb')

    def values(self):
        """Used for JSON serializing. Must be a better way to do this. :-("""
        return dict(id   = self.id,
                    url  = self.url,
                    name = self.name,
                    name_full = self.name_full,
                    born = self.born.isoformat(),
                    picture_hash = self.picture_hash,
                    gender = self.gender,
                    region_id = self.region_id,
                    polit_group_id = self.polit_group_id)

class ParlMembVoting(Base):
    __tablename__ = 'parl_memb_voting'
    __table_args__ = (
                      UniqueConstraint('parl_memb_id', 'voting_id'),
                      Index('ix_pmv_parl_memb_id', 'parl_memb_id'),
                      Index('ix_pmv_voting_id', 'voting_id'),
                      )

    id = Column(Integer, primary_key=True)
    vote = Column(String(1))
    parl_memb_id = Column(Integer, ForeignKey('parl_memb.id'))
    voting_id = Column(Integer, ForeignKey('voting.id'))

    def values(self):
        """Used for JSON serializing. Must be a better way to do this. :-("""
        return dict(id           = self.id,
                    vote         = self.vote,
                    parl_memb_id = self.parl_memb_id,
                    voting_id    = self.voting_id)

class UserVoting(Base):
    __tablename__ = 'user_voting'
    __table_args__ = (
                      UniqueConstraint('user_id', 'voting_review_id'),
                      Index('ix_uv_user_id', 'user_id'),
                      Index('ix_uv_voting_review_id', 'voting_review_id'),
                      )

    id = Column(Integer, primary_key=True)
    vote = Column(String(1))
    user_id = Column(Integer, ForeignKey('app_user.id'))
    voting_review_id = Column(Integer, ForeignKey('voting_review.id'))
    created = Column(DateTime, server_default=func.now())

    def values(self):
        """Used for JSON serializing. Must be a better way to do this. :-("""
        return dict(id               = self.id,
                    vote             = self.vote,
                    user_id          = self.user_id,
                    voting_review_id = self.voting_review_id)

class VotingReview(Base):
    __tablename__ = 'voting_review'
    __table_args__ = (
                      UniqueConstraint('voting_id', 'user_id'),
                      Index('ix_vr_user_id', 'user_id'),
                      )
    id = Column(Integer, primary_key=True)
    title = Column(String(160))
    reasoning = Column(String)
    voting_id = Column(Integer, ForeignKey('voting.id'))
    user_id = Column(Integer, ForeignKey('app_user.id'))
    vote_sugg = Column(String(1))
    created = Column(DateTime, server_default=func.now())

    userVotings = relationship('UserVoting', backref='votingReview')

    def values(self):
        """Used for JSON serializing. Must be a better way to do this. :-("""
        return dict(id           = self.id,
                    title        = self.title,
                    reasoning    = self.reasoning,
                    voting_id    = self.voting_id,
                    user_id      = self.user_id,
                    vote_sugg    = self.vote_sugg)

class User(Base):
    __tablename__ = 'app_user'
    __table_args__ = (
                      Index('ix_usr_fb_id', 'fb_id'),
                      )
    id = Column(Integer, primary_key=True)
    fb_id = Column(BigInteger, unique=True)
    name = Column(String(255))
    first_name = Column(String(55))
    last_name = Column(String(200))
    url = Column(String(4000))
    gender = Column(String(10))
    created = Column(DateTime, server_default=func.now())
    last_modified = Column(DateTime, default=func.now)

    votingReviews = relationship('VotingReview', backref='user')
    userVotings = relationship('UserVoting', backref='user')

    def values(self):
        """Used for JSON serializing. Must be a better way to do this. :-("""
        return dict(fb_id         = self.fb_id,
                    name          = self.name,
                    first_name    = self.first_name,
                    last_name     = self.last_name,
                    url           = self.url,
                    gender        = self.gender,
                    created       = self.created.isoformat(),
                    last_modified = self.last_modified.isoformat())

class Region(Base):
    __tablename__ = 'region'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    url = Column(String(4000), unique=True)

    parlMembs = relationship('ParlMemb', backref='region')

    def values(self):
        """Used for JSON serializing. Must be a better way to do this. :-("""
        return dict(name          = self.name,
                    url           = self.url)

class PolitGroup(Base):
    __tablename__ = 'polit_group'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    name_full = Column(String(512))
    url = Column(String(4000), unique=True)

    parlMembs = relationship('ParlMemb', backref='polit_group')

    def values(self):
        """Used for JSON serializing. Must be a better way to do this. :-("""
        return dict(name          = self.name,
                    name_full     = self.name_full,
                    url           = self.url)
