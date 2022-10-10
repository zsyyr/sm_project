
from selenium.webdriver.common.by import By
import logging
import datetime_util
from .extractor import Extractor
import post.wb_post as wb_post
import uuid

from importlib import reload
reload(datetime_util)
reload(wb_post)

logger = logging.getLogger('crawler.wb_extractor')

class WbExtractor(Extractor):
    def __init__(self, driver):
        self.driver = driver 
        self.page_source = ''       
        self.etree = ''
        self.post_list_xpath = '//div[@id="scroller"]/div/div'
        self.post_time_xpath = './/a[@class="head-info_time_6sFQg"]'
        self.post_content_xpath = './/div[@class="detail_wbtext_4CRf9"]'
        self.post_up_n_xpath = ''
        self.post_retweet_n_xpath = './/footer'
        self.post_comment_n_xpath = ''

    def extract_post_list(self, driver):
        try:
            return driver.find_elements(By.XPATH, self.post_list_xpath)
        except Exception as e:
            logger.exception(e)
            return []
    
    def extract_post_time(self, post_el):
        post_time_xpath = ""
        try:
            post_time_el = post_el.find_element(By.XPATH, self.post_time_xpath)
            post_time_str = post_time_el.get_attribute('title')
            post_time = datetime_util.parse_time(post_time_str)
            logging.debug(post_time_el.text + " " + post_time_str)
            return post_time
        except Exception as e:
            logger.exception(e)
            return 0
            
    def extract_post_content(self, post_div):
        post_content_xpath = ""
        try:
            post_content_el = post_div.find_element(By.XPATH, self.post_content_xpath)
            logging.debug(post_content_el.text)
            return post_content_el.text
        except Exception as e:
            logger.exception(e)
            return ''
            
    # def extract_post_up_number(self, post_div):
    #     post_up_n_xpath = ""
    #     try:
    #         return post_div.find_element(By.XPATH, self.post_up_n_xpath)
    #     except Exception as e:
    #         logger.exception(e)
            
    def extract_post_retweet_number(self, post_div):
        post_retweet_n_xpath = ""
        try:
            return post_div.find_element(By.XPATH, self.post_retweet_n_xpath)
            # post_footer_el.text.split('\n')
        except Exception as e:
            logger.exception(e)
            
    # def extract_post_comment_number(self, post_div):
    #     post_comment_n_xpath = ""
    #     try:
    #         return post_div.find_element(By.XPATH, self.post_comment_n_xpath)
    #     except Exception as e:
    #         logger.exception(e)

    

    def extract_account_posts(self, driver, account, _a, _b, _c, _d):
        logger.info("start extract weibo account posts")
        post_list = []
        DATE_CHECK = True
        post_el_list = self.extract_post_list(driver)
        # logger.debug(len(post_el_list))
        for i in range(len(post_el_list)): 
            print(f'************index:{self.element_index}************')                    
            print(f'************i:{i}************')          
            print(f'************post list len:{len(post_el_list)}************')        
            # if i <= self.element_index:
            #     pass
            # else:
                  
            post_el = post_el_list[i]
            self.element_index = i      
            post = wb_post.WbPost() 
            try:
                post.publish_time = self.extract_post_time(post_el)
                # DATE_CHECK = datetime_util.check_date(post.publish_time, account.stop_date)
                if not DATE_CHECK:
                    break
            except Exception as e:
                post.publish_time = ''
                logger.exception(e)
            try:
                post.content = self.extract_post_content(post_el)
            except Exception as e:
                post.content = ''
                logger.exception(e)

            post_footer_el = self.extract_post_retweet_number(post_el)
            try:
                number_list = post_footer_el.text.split('\n')
            except:
                number_list = []
            print(number_list)
            try:
                post.retweet_num = number_list[0]
                post.comment_num = number_list[1]
                post.up_num = number_list[2]
            except IndexError:
                post.retweet_num = ''
                post.comment_num = ''
                post.up_num = ''
            # try:    
            #     post.up_num = self.extract_post_up_number(post_div)
            # except Exception as e:
            #     post.up_num = 0
            #     logger.exception(e)
            # try:
            #     post.retweet_num = self.extract_post_retweet_number(post_div)
            # except Exception as e:
            #     post.retweet_num = 0
            #     logger.exception(e)
            # try:
            #     post.comment_num = self.extract_post_comment_number(post_div)
            # except Exception as e:
            #     post.comment_num = 0
            #     logger.exception(e)
            if post.content:
                post.uuid = str(uuid.uuid3(uuid.NAMESPACE_OID, post.content))
            else:
                post.uuid = 0
            post.account = account.name
            post_list.append(post)
        return post_list, [], DATE_CHECK , True



    
