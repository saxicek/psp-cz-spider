# Scrapy settings for psp_cz project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#
import os

BOT_NAME = 'psp_cz'

SPIDER_MODULES = ['psp_cz.spiders']
NEWSPIDER_MODULE = 'psp_cz.spiders'
DEFAULT_ITEM_CLASS = 'scrapy.item.Item'
ITEM_PIPELINES = ['scrapy.contrib.pipeline.images.ImagesPipeline', 'psp_cz.pipelines.DBStorePipeline']
WEBSERVICE_ENABLED = False
TELNETCONSOLE_ENABLED = False
IMAGES_STORE = os.environ['IMAGES_STORE']
IMAGES_THUMBS = {
    'small': (50, 50),
}
