# coding=utf-8
#
# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/topics/items.html

from scrapy.item import Item, Field

class ParlMembVote(Item):
    # unique identifier for duplicity check
    id = Field()

    # vote of the parliament member in the voting
    vote = Field()

    # URL to parliament member
    parl_memb_url = Field()

    # short name of the parliament member
    parl_memb_name = Field()

    # reference to the voting
    voting_id = Field()


class Voting(Item):
    # unique identifier for duplicity check
    id = Field()

    # URL of the voting
    url = Field()

    # name of the voting - sequential numbers are used
    name = Field()

    # reference to the sitting
    sitting_id = Field()


class Sitting(Item):
    # unique identifier for duplicity check
    id = Field()

    # URL of the sitting
    url = Field()

    # name of the sitting - sequential numbers along with text 'schůze' are being used
    name = Field()
