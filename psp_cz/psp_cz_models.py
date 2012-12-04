# coding=utf-8
from sqlalchemy import func, Column, Integer, String, Date, DateTime
from sqlalchemy.orm import relationship, object_mapper, ColumnProperty
from sqlalchemy.schema import ForeignKey, UniqueConstraint, Index
import datetime

from . import Base

class BaseMixin(object):
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, nullable=False, server_default=func.now())
    last_modified = Column(DateTime, nullable=False, default=func.now())

    def values(self):
        """JSON serialization of model attributes.

        """
        columns = (p.key for p in object_mapper(self).iterate_properties
                   if isinstance(p, ColumnProperty))
        result = dict((col, getattr(self, col)) for col in columns)
        # Convert datetime and date objects to ISO 8601 format.
        #
        # TODO: We can get rid of this in Flask 0.9.
        # https://github.com/mitsuhiko/flask/pull/471
        for key, value in result.items():
            if isinstance(value, datetime.date):
                result[key] = value.isoformat()

        return result

class Sitting(BaseMixin, Base):
    __tablename__ = 'sitting'
    __table_args__ = (
                      Index('ix_sit_url', 'url'),
                      )

    url = Column(String(4000), unique=True, nullable=False)
    name = Column(String(255), nullable=False)

    votings = relationship('Voting', backref='sitting')

class Voting(BaseMixin, Base):
    __tablename__ = 'voting'
    __table_args__ = (
                      Index('ix_vot_url', 'url'),
                      Index('ix_vot_sitting_id', 'sitting_id'),
                      Index('ix_vot_voting_date', 'voting_date')
                      )

    url = Column(String(4000), unique=True, nullable=False)
    voting_nr = Column(Integer)
    name = Column(String(500), nullable=False)
    voting_date = Column(Date, nullable=False)
    minutes_url = Column(String(4000))
    result = Column(String(50), nullable=False)
    sitting_id = Column(Integer, ForeignKey('sitting.id'), nullable=False)

    parlMembVotings = relationship('ParlMembVoting', backref='voting')

class ParlMemb(BaseMixin, Base):
    __tablename__ = 'parl_memb'
    __table_args__ = (
                      UniqueConstraint('psp_cz_id'),
                      Index('ix_pm_url', 'url'),
                      )

    url = Column(String(4000), unique=True, nullable=False)
    name = Column(String(255))
    name_full = Column(String(255))
    born = Column(Date)
    picture_hash = Column(String(40)) # using SHA1 hash as picture identifier
    gender = Column(String(1))
    region_id = Column(Integer, ForeignKey('region.id'))
    polit_group_id = Column(Integer, ForeignKey('polit_group.id'))
    psp_cz_id = Column(Integer, nullable=False)

    parlMembVotings = relationship('ParlMembVoting', backref='parlMemb')

class ParlMembVoting(BaseMixin, Base):
    __tablename__ = 'parl_memb_voting'
    __table_args__ = (
                      UniqueConstraint('parl_memb_id', 'voting_id'),
                      Index('ix_pmv_parl_memb_id', 'parl_memb_id'),
                      Index('ix_pmv_voting_id', 'voting_id'),
                      )

    vote = Column(String(1), nullable=False)
    parl_memb_id = Column(Integer, ForeignKey('parl_memb.id'), nullable=False)
    voting_id = Column(Integer, ForeignKey('voting.id'), nullable=False)

class Region(BaseMixin, Base):
    __tablename__ = 'region'

    name = Column(String(255), nullable=False)
    url = Column(String(4000), unique=True, nullable=False)

    parlMembs = relationship('ParlMemb', backref='region')

class PolitGroup(BaseMixin, Base):
    __tablename__ = 'polit_group'

    name = Column(String(255), nullable=False)
    name_full = Column(String(512), nullable=False)
    url = Column(String(4000), unique=True, nullable=False)

    parlMembs = relationship('ParlMemb', backref='polit_group')
