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
    voting = Field()


class Voting(Item):
    # unique identifier for duplicity check
    id = Field()

    # URL of the voting
    url = Field()

    # sequential voting number
    voting_nr = Field()

    # name of the voting
    name = Field()

    # date of the voting
    voting_date = Field()

    # link to the voting transcription
    minutes_url = Field()

    # voting result in textual form
    result = Field()

    # reference to the sitting
    sitting = Field()


class Sitting(Item):
    # unique identifier for duplicity check
    id = Field()

    # URL of the sitting
    url = Field()

    # name of the sitting - sequential numbers along with text 'schuze' are being used
    name = Field()
