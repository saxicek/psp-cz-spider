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
from psp_cz.psp_cz_models import Sitting as TSitting

class PspCzSpider(CrawlSpider):
    """
    Spider gets information about parliament sittings, votings, parliament
    members (not complete information - poslanci.psp.cz spider gets it) and
    about voting of each parliament member.

    Spider accepts following parameters:
        mode - values 'incremental' or 'full'. Incremental is the default.
            Completely parses the information from psp.cz. For incremental mode
            there are 2 possible run options - either parameters from_term and
            from_sitting are specified and then parsing starts at the sitting
             specified and continues until the latest sitting. If from_term or
             from_sitting is not specified then spider gets the latest parsed
             sitting from the database and starts with this sitting (the latest
             sitting from the database is crawled again to make sure that the
             previously fetched information is complete).
        from_term - term of parliament. Applicable only if mode=incremental and
            from_sitting parameter is also specified
        from_sitting - sitting number we should start at with parsing. It is
            applicable only for incremental mode and from_term parameter
            specified.

    """
    name = "psp.cz"
    allowed_domains = ["www.psp.cz"]
    start_urls = [
        "http://www.psp.cz/sqw/hp.sqw?k=27",
        "http://www.psp.cz/sqw/hlasovani.sqw?zvo=1"
    ]
    # restriction not to parse all data over and over again
    SITTING_URL_SORT_REGEXP = r'o=([:0-9:]+)\&s=([:0-9:]+)'

    rules = (
        # extract sittings
        Rule(SgmlLinkExtractor(allow=('hlasovani\.sqw$')), callback='parse_sittings', follow=False),
    )

    def __init__(self, *a, **kw):
        super(PspCzSpider, self).__init__(*a, **kw)

        if kw.get('mode', None) in ['full', 'incremental']:
            self.mode = kw['mode']
        else:
            self.mode = 'incremental'

        if self.mode == 'incremental':
            from_sitting = kw.get('from_sitting', None)
            from_term = kw.get('from_term', None)
            if not from_sitting or not from_term:
                # get the latest Sitting urls from the database
                db_sitting_urls = db_session.query(TSitting.url).all()

                if db_sitting_urls:
                    # sort the list
                    db_sitting_urls.sort(key=lambda x: map(int, re.findall(self.SITTING_URL_SORT_REGEXP, x[0])[0]))
                    latest_db_sitting_url = db_sitting_urls[-1][0]
                    self.log('Latest URL in DB is ' + latest_db_sitting_url)
                    self.start_from = map(int, re.findall(self.SITTING_URL_SORT_REGEXP, latest_db_sitting_url)[0])
                else:
                    # no starting point specified and no sitting record in DB - switch to 'full' mode
                    self.mode = 'full'
            else:
                self.start_from = [int(from_term), int(from_sitting)]

    def parse_sittings(self, response):
        """ Parses parliament sittings at the current season """

        hxs = HtmlXPathSelector(response)
        base_url = get_base_url(response)

        sitting_links = hxs.select('//*[@id="main-content"]/div[1]/table/tbody/tr/td[1]/b')

        for sitting_link in sitting_links:
            sitting = Sitting()
            relative_url = sitting_link.select('a/@href').extract()[0]
            sitting['url'] = urljoin_rfc(base_url, relative_url)
            sitting['id'] = sitting['url']
            sitting['name'] = sitting_link.select('a/text()').extract()[0]

            # to optimize speed start downloading only from latest sitting stored in DB
            if self.mode == 'full' or \
                    map(int, re.findall(self.SITTING_URL_SORT_REGEXP, sitting['url'])[0]) >= self.start_from:
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

        voting_links = hxs.select('//*[@id="main-content"]/div[1]/center/table/tr[position()>1]')

        for voting_link in voting_links:
            voting = Voting()
            relative_url = voting_link.select('td[2]/a/@href').extract()[0]
            voting['url'] = urljoin_rfc(base_url, relative_url)
            voting['id'] = voting['url']
            voting['voting_nr'] = int(voting_link.select('td[2]/a/text()').extract()[0])
            voting['name'] = voting_link.select('td[4]/node()').extract()[0]
            if voting_link.select('td[5]/a/text()'):
                date_text = voting_link.select('td[5]/a/text()').extract()[0].replace(u'\xa0', '')
                voting['voting_date'] = datetime.strptime(date_text, '%d.%m.%Y')
                voting['minutes_url'] = voting_link.select('td[5]/a/@href').extract()[0]
            else:
                date_text = voting_link.select('td[5]/text()').extract()[0].replace(u'\xa0', '')
                voting['voting_date'] = datetime.strptime(date_text, '%d.%m.%Y')
                voting['minutes_url'] = None
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

        votings = hxs.select('//ul[@class="results"]//li')

        for v in votings:
            parl_memb_vote = ParlMembVote()
            parl_memb_vote['vote'] = v.select('span/text()').extract()[0]
            parl_memb_vote['parl_memb_name'] = v.select('a/text()').extract()[0]
            relative_url = v.select('a/@href').extract()[0]
            # remove &o=<number> parameter - it refers to tenure
            relative_url = re.sub(r'\&o=[:0-9:]+', '', relative_url)
            parl_memb_vote['parl_memb_url'] = urljoin_rfc(base_url, relative_url)
            parl_memb_vote['id'] = response.url + '|' + parl_memb_vote['parl_memb_url']
            parl_memb_vote['voting'] = voting
            yield parl_memb_vote
