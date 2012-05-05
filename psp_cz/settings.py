# Scrapy settings for psp_cz project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'psp_cz'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['psp_cz.spiders']
NEWSPIDER_MODULE = 'psp_cz.spiders'
DEFAULT_ITEM_CLASS = 'scrapy.item.Item'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
ITEM_PIPELINES = ['scrapy.contrib.pipeline.images.ImagesPipeline', 'psp_cz.pipelines.DBStorePipeline']
WEBSERVICE_ENABLED = False
TELNETCONSOLE_ENABLED = False
IMAGES_STORE = 'd:/devel/moji-poslanci/static/images/mp'
IMAGES_THUMBS = {
    'small': (50, 50),
}
