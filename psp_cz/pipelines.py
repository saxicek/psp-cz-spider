import re

from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.exceptions import DropItem
from psp_cz.database import db_session, init_db
from psp_cz.items import ParlMembVote, Voting, Sitting
from psp_cz.models import Voting as TVoting, ParlMemb as TParlMemb, ParlMembVoting as TParlMembVoting, Sitting as TSitting

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/topics/item-pipeline.html

class DuplicatesPipeline(object):
    def __init__(self):
        self.duplicates = {}
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_opened(self, spider):
        self.duplicates[spider] = set()

    def spider_closed(self, spider):
        del self.duplicates[spider]

    def process_item(self, item, spider):
        if item['id'] in self.duplicates[spider]:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.duplicates[spider].add(item['id'])

            return item


class DBStorePipeline(object):
    def __init__(self):
        dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_opened(self, spider):
        init_db()

        if spider.latest_db_sitting_url == None:
            # get the latest Sitting urls from the database
            db_sitting_urls = db_session.query(TSitting.url).all()

            if db_sitting_urls:
                # sort the list
                db_sitting_urls.sort(key=lambda x: map(int, re.findall(spider.SITTING_URL_SORT_REGEXP, x[0])[0]))
                spider.latest_db_sitting_url = db_sitting_urls[-1][0]
                spider.log('Latest URL in DB is ' + spider.latest_db_sitting_url)

    def spider_closed(self, spider):
        db_session.close()

    def process_item(self, item, spider):
        if isinstance(item, Sitting):
            if self.get_db_sitting(item) == None:
                sitting = TSitting(url = item['url'],
                                   name = item['name'])
                db_session.add(sitting)
                db_session.commit()

        elif isinstance(item, Voting):
            if self.get_db_voting(item) == None:
                voting = TVoting(url = item['url'],
                                 voting_nr = item['voting_nr'],
                                 name = item['name'],
                                 voting_date = item['voting_date'],
                                 minutes_url = item['minutes_url'],
                                 result = item['result'],
                                 sitting = self.get_db_sitting(item['sitting']))
                db_session.add(voting)
                db_session.commit()

        elif isinstance(item, ParlMembVote):
            if self.get_db_parl_memb_vote(item) == None:
                # check if parliament member exists; create one if not
                parl_memb = self.get_db_parl_memb(item)
                if parl_memb == None:
                    parl_memb = TParlMemb(url = item['parl_memb_url'],
                                          name = item['parl_memb_name'])
                    db_session.add(parl_memb)
                    db_session.commit()

                parl_memb_voting = TParlMembVoting(vote = item['vote'],
                                                   parlMemb = parl_memb,
                                                   voting = self.get_db_voting(item['voting']))
                db_session.add(parl_memb_voting)
                db_session.commit()

        return item

    def get_db_sitting(self, item):
        """Helper procedure that fetches DB Sitting entity based on Sitting Item"""
        if isinstance(item, Sitting):
            return db_session.query(TSitting).filter_by(url=item['url']).first()

    def get_db_voting(self, item):
        """Helper procedure that fetches DB Voting entity based on Voting Item"""
        if isinstance(item, Voting):
            return db_session.query(TVoting).filter_by(url=item['url']).first()

    def get_db_parl_memb(self, item):
        """Helper procedure that fetches DB ParlMemb entity based on ParlMembVote Item"""
        if isinstance(item, ParlMembVote):
            return db_session.query(TParlMemb).filter_by(url=item['parl_memb_url']).first()

    def get_db_parl_memb_vote(self, item):
        """Helper procedure that fetches DB ParlMembVote entity based on ParlMembVote Item"""
        if isinstance(item, ParlMembVote):
            return db_session.query(TParlMembVoting).filter_by(parlMemb=self.get_db_parl_memb(item),
                                                             voting=self.get_db_voting(item['voting'])).first()

