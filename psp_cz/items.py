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

    # parliament member id in psp.cz
    parl_memb_id = Field()


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


class ParlMemb(Item):
    # unique identifier for duplicity check
    id = Field()

    # url of the parliament member
    url = Field()

    # parliament member region
    region = Field()

    # URL to parliament member region
    region_url = Field()

    # short name of the parliament political group
    group = Field()

    # short name of the parliament political group
    group_long = Field()

    # parliament political group URL
    group_url = Field()

    # parliament member name
    name = Field()

    # date born
    born = Field()

    # picture hash
    picture_hash = Field()

    # gender
    gender = Field()

    # parliament member id in psp.cz
    parl_memb_id = Field()
    
    # image urls, images - used by ImagesPipeline
    # see http://doc.scrapy.org/en/latest/topics/images.html
    image_urls = Field()
    images = Field()
