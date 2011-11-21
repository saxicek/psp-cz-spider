from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.exceptions import DropItem
from psp_cz.items import ParlMembVote, Voting

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
