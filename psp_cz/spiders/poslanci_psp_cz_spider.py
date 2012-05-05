# coding=utf-8
import re

from datetime import datetime
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc

from psp_cz.database import db_session
from psp_cz.items import ParlMemb

class PoslanciPspCzSpider(CrawlSpider):
    """ Spider crawls the psp.cz and gets information about parliament members """
    name = "poslanci.psp.cz"
    allowed_domains = ["www.psp.cz"]

    # we will start from "Poslanecké kluby" page
    start_urls = [
        "http://www.psp.cz/sqw/organy2.sqw?k=1"
    ]

    rules = (
        # follow links to parliamentary political groups
        Rule(SgmlLinkExtractor(allow=('\/snem.sqw',)), callback='parse_parl_polit_groups', follow=False),
    )

    def parse_parl_polit_groups(self, response):
        """ Parses parliament political groups """

        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        memb_links = hxs.select('/html/body/div[3]/div[2]/div[2]/table/tbody/tr')

        for member_link in memb_links:
            region = member_link.select('td[4]/a/text()').extract()[0]
            region_url = urljoin_rfc(base_url, member_link.select('td[4]/a/@href').extract()[0])
            group = member_link.select('td[6]/a/text()').extract()[0]
            group_long = member_link.select('td[6]/a/@title').extract()[0]
            group_url = urljoin_rfc(base_url, member_link.select('td[6]/a/@href').extract()[0])
            request_url = urljoin_rfc(base_url, member_link.select('td[2]/a/@href').extract()[0])

            request = Request(request_url,
                              self.parse_parl_memb,
                              meta={'id':request_url,
                                    'url':request_url,
                                    'region':region,
                                    'region_url':region_url,
                                    'group':group,
                                    'group_long':group_long,
                                    'group_url':group_url})
            yield request


    # this callback just adds sitting info to requests and follows links
    def parse_parl_memb(self, response):
        """ Parses parliament member info """

        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        picture_relative_url = hxs.select('/html/body/div[3]/div[2]/div[2]/table/tr/td[2]/a/img/@src').extract()[0]
        # There is one exception when Miroslava Němcová has her birth date not in 4th cell
        # but in the 2nd. Unfortunate, but whatever, I can get over it... 
        born_n_gender = hxs.select('/html/body/div[3]/div[2]/div[2]/table/tr').select('//td/text()').re(r'(Narozen.*)')[0]
        gender = None
        if born_n_gender.find('Narozen:') != -1:
            gender = 'M'
        elif born_n_gender.find('Narozena:') != -1:
            gender = 'F'

        born = datetime.strptime(born_n_gender.split(' ', 1)[1], '%d.\xc2\xa0%m.\xc2\xa0%Y')

        parl_memb = ParlMemb()
        parl_memb['id']          = response.meta['id']
        parl_memb['url']         = response.meta['url']
        parl_memb['region']      = response.meta['region']
        parl_memb['region_url']  = response.meta['region_url']
        parl_memb['group']       = response.meta['group']
        parl_memb['group_long']  = response.meta['group_long']
        parl_memb['group_url']   = response.meta['group_url']
        parl_memb['name']        = hxs.select('/html/body/div[3]/div/h2/text()').extract()[0]
        parl_memb['born']        = born
        parl_memb['gender']      = gender
        parl_memb['image_urls']  = [urljoin_rfc(base_url, picture_relative_url)]

        yield parl_memb
