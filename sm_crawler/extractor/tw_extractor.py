from socket import TIPC_MEDIUM_IMPORTANCE
from selenium.webdriver.common.by import By
import logging
import datetime
import datetime_util
import util
from .extractor import Extractor
from post.fb_post import FbPost

from importlib import reload
reload(datetime_util)

logger = logging.getLogger('crawler.fb_extractor')

@util.Singleton
class TwExtractor(Extractor):
   pass 
    
