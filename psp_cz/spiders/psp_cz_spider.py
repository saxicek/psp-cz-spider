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
from psp_cz.items import ParlMembVote, Voting, Sitting
from psp_cz.models import Sitting as TSitting

class PspCzSpider(CrawlSpider):
    name = "psp.cz"
    allowed_domains = ["www.psp.cz"]
    start_urls = [
        "http://www.psp.cz/sqw/hp.sqw?k=27"
    ]
    latest_db_sitting_url = None
    SITTING_URL_SORT_REGEXP = r'o=([:0-9:]+)\&s=([:0-9:]+)'

    rules = (
        # extract sittings
        Rule(SgmlLinkExtractor(allow=('hlasovani\.sqw$')), callback='parse_sittings', follow=False),
    )

    def parse_sittings(self, response):
        """ Parses parliament sittings at the current season """

        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        sitting_links = hxs.select('/html/body/div[3]/div[2]/div[2]/b')

        for sitting_link in sitting_links:
            sitting = Sitting()
            relative_url = sitting_link.select('a/@href').extract()[0]
            sitting['url'] = urljoin_rfc(base_url, relative_url)
            sitting['id'] = sitting['url']
            sitting['name'] = sitting_link.select('a/text()').extract()[0]

            # to optimize speed start downloading only from latest sitting stored in DB
            if self.latest_db_sitting_url == None or \
                    map(int, re.findall(self.SITTING_URL_SORT_REGEXP, sitting['url'])[0]) >= \
                    map(int, re.findall(self.SITTING_URL_SORT_REGEXP, self.latest_db_sitting_url)[0]):
                self.log('PARSE ' + sitting['url'])
                yield sitting

                request = Request(sitting['url'], self.proceed_to_votings, meta={'sitting':sitting})
                yield request

            else:
                self.log('SKIP ' + sitting['url'])


    # this callback just adds sitting info to requests and follows links
    def proceed_to_votings(self, response):
        """ Navigates from more descriptive page about votings to voting table """

        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        if 'sitting' in response.meta:
            sitting = response.meta['sitting']
        else:
            self.log('Error: SITTING parameter not found! %s' % response.url)
            return

        voting_links = hxs.select('//@href').re(r'phlasa\.sqw.*')

        for voting_link in voting_links:
            request = Request(urljoin_rfc(base_url, voting_link),
                              self.parse_votings,
                              meta={'sitting':sitting})
            yield request


    def parse_votings(self, response):
        """ Parses votings from given parliament sitting """

        hxs = HtmlXPathSelector(response)

        base_url = get_base_url(response)
        if 'sitting' in response.meta:
            sitting = response.meta['sitting']
        else:
            self.log('Error: SITTING parameter not found! %s' % response.url)
            return

        voting_links = hxs.select('/html/body/div[3]/div[2]/div[2]/center/table/tr[position()>1]')

        for voting_link in voting_links:
            voting = Voting()
            relative_url = voting_link.select('td[2]/a/@href').extract()[0]
            voting['url'] = urljoin_rfc(base_url, relative_url)
            voting['id'] = voting['url']
            voting['voting_nr'] = int(voting_link.select('td[2]/a/text()').extract()[0])
            voting['name'] = voting_link.select('td[4]/node()').extract()[0]
            voting['voting_date'] = datetime.strptime(voting_link.select('td[5]/a/text()').extract()[0], '%d.\xc2\xa0%m.\xc2\xa0%Y')
            voting['minutes_url'] = voting_link.select('td[5]/a/@href').extract()[0]
            voting['result'] = voting_link.select('td[6]/text()').extract()[0]
            voting['sitting'] = sitting
            yield voting

            request = Request(voting['url'], self.parse_parl_memb_votes, meta={'voting':voting})
            yield request


    def parse_parl_memb_votes(self, response):
        """ Parses votes of individual members of parliament """

        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)
        if 'voting' in response.meta:
            voting = response.meta['voting']
        else:
            self.log('Error: VOTING parameter not found! %s' % response.url)
            return

        voting_rows = hxs.select('/html/body/div[3]/div[2]/div[2]/center[2]/table/tr[position()>1]')

        for voting_row in voting_rows:
            self.log(voting_row)
            # 1st vote on the row
            if voting_row.select('td[2]/a/@href'):
                parl_memb_vote = ParlMembVote()
                parl_memb_vote['vote'] = voting_row.select('td[1]/text()').extract()[0]
                parl_memb_vote['parl_memb_name'] = voting_row.select('td[2]/a/text()').extract()[0]
                relative_url = voting_row.select('td[2]/a/@href').extract()[0]
                parl_memb_vote['parl_memb_url'] = urljoin_rfc(base_url, relative_url)
                parl_memb_vote['id'] = response.url + '|' + parl_memb_vote['parl_memb_url']
                parl_memb_vote['voting'] = voting
                yield parl_memb_vote

            # 2nd vote on the row
            if voting_row.select('td[4]/a/@href'):
                parl_memb_vote = ParlMembVote()
                parl_memb_vote['vote'] = voting_row.select('td[3]/text()').extract()[0]
                parl_memb_vote['parl_memb_name'] = voting_row.select('td[4]/a/text()').extract()[0]
                relative_url = voting_row.select('td[4]/a/@href').extract()[0]
                parl_memb_vote['parl_memb_url'] = urljoin_rfc(base_url, relative_url)
                parl_memb_vote['id'] = response.url + '|' + parl_memb_vote['parl_memb_url']
                parl_memb_vote['voting'] = voting
                yield parl_memb_vote

            # 3rd vote on the row
            if voting_row.select('td[6]/a/@href'):
                parl_memb_vote = ParlMembVote()
                parl_memb_vote['vote'] = voting_row.select('td[5]/text()').extract()[0]
                parl_memb_vote['parl_memb_name'] = voting_row.select('td[6]/a/text()').extract()[0]
                relative_url = voting_row.select('td[6]/a/@href').extract()[0]
                parl_memb_vote['parl_memb_url'] = urljoin_rfc(base_url, relative_url)
                parl_memb_vote['id'] = response.url + '|' + parl_memb_vote['parl_memb_url']
                parl_memb_vote['voting'] = voting
                yield parl_memb_vote

            # 4th vote on the row
            if voting_row.select('td[8]/a/@href'):
                parl_memb_vote = ParlMembVote()
                parl_memb_vote['vote'] = voting_row.select('td[7]/text()').extract()[0]
                parl_memb_vote['parl_memb_name'] = voting_row.select('td[8]/a/text()').extract()[0]
                relative_url = voting_row.select('td[8]/a/@href').extract()[0]
                parl_memb_vote['parl_memb_url'] = urljoin_rfc(base_url, relative_url)
                parl_memb_vote['id'] = response.url + '|' + parl_memb_vote['parl_memb_url']
                parl_memb_vote['voting'] = voting
                yield parl_memb_vote

