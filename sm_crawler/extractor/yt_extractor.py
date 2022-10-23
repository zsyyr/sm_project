from lzma import CHECK_SHA256
import platform
sys = platform.system()
if sys == 'Linux':
    from socket import TIPC_MEDIUM_IMPORTANCE
    
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import logging
import datetime, time
import datetime_util
import util
from .extractor import Extractor
from post.yt_post import YtPost
from comment.yt_comment import YtComment

from importlib import reload
reload(datetime_util)
logger = logging.getLogger('crawler.yt_extractor')

# @util.Singleton
class YtExtractor(Extractor):
    def __init__(self, driver): 
        self.driver = driver
        self.page_source = ''         
        self.etree = ''
        self.post_el = None
        self.element_index = 0 
        self.comment_el_len = -1
        self.video_info_flag = 1
        self.uuid = ''
        self.extract_time = datetime.datetime.now()
        self.video_account_xpath = '//div[@id="upload-info"]//a'
        self.video_title_xpath = '//div[@id="info-contents"]//h1'
        self.viedo_description_xpath = '//div[@id="meta-contents"]//div[@id="description"]'
        self.video_publish_time_xpath = '//div[@id="info-strings"]'
        self.video_up_num_xpath = '//div[@id="menu-container"]//div[@id="top-level-buttons-computed"]//yt-formatted-string'
        self.video_views_num_xpath = '//div[@id="info"]//div[@id="container"]//ytd-video-view-count-renderer/span[2]'
        self.video_comment_num_xpath = '//ytd-comments[@id="comments"]//h2'

        self.video_comments_xpath = '//*[@id="comments"]//div[@id="contents"]//*[@id="comment"]'
        self.comment_author_xpath = './/*[@id="author-text"]/span'
        self.comment_publish_time_xpath = './/*[@class="published-time-text style-scope ytd-comment-renderer"]'
        self.comment_content_xpath = './/*[@id="content-text"]'
        self.comment_up_num_xpath = './/*[@id="vote-count-middle"]'
        self.comment_retweet_num_xpath = './/*[@id="more-replies"]//*[@id="button"]'
        # self.comment_retweet_num_xpath = './/*[@id="more-replies"]//*[@id="button"]//yt-formatted-string[@id="text"]'
        

        
    
    def auto_scroll(self, sleep_s=10):
        temp_height = 0
        while True:
            # 循环将滚动条下拉
            self.driver.execute_script("window.scrollBy(0,2000)")
            # sleep一下让滚动条反应一下
            time.sleep(sleep_s)
            check_height = self.driver.execute_script(
                "return document.documentElement.scrollTop || window.pageYOffset || document.body.scrollTop;")
            # 如果两者相等说明到底了
            if check_height == temp_height:
                break
            temp_height = check_height
            print(check_height)
        print("页面已拉到底")     

    def extract_video_info(self):
        info = YtPost()
        try:
            self.driver.execute_script("window.scrollBy(0,500)")
            time.sleep(10)
            info.account = self.driver.find_element(by=By.XPATH, value=self.video_account_xpath).text
            info.content = self.driver.find_element(by=By.XPATH, value=self.video_title_xpath).text
            info.news_description = self.driver.find_element(by=By.XPATH, value=self.viedo_description_xpath).text
            publish_time_str = self.driver.find_element(by=By.XPATH, value=self.video_publish_time_xpath).text
            up_num_str = self.driver.find_element(by=By.XPATH, value=self.video_up_num_xpath).text
            views_str = self.driver.find_element(by=By.XPATH, value=self.video_views_num_xpath).text
            try:
                comment_num = self.driver.find_element(by=By.XPATH, value=self.video_comment_num_xpath).text.split()[0]
            except NoSuchElementException as e:
                time.sleep(30)
                comment_num = self.driver.find_element(by=By.XPATH, value=self.video_comment_num_xpath).text.split()[0]
                if not comment_num:                    
                    raise Exception
                # logger.exception(e)
            info.publish_time = publish_time_str
            info.up_num = util.parse_number(up_num_str)
            info.views_num = util.parse_number(views_str)
            info.uuid = util.gen_uuid(info.content)
            self.uuid = info.uuid
            info.crawling_time = self.extract_time.strftime(r'%Y-%m-%d')
            info.comment_num = util.parse_number(comment_num)
            print(info.__dict__)
            return info, True
        except Exception as e:
            logger.error(e)
            return None, False
        finally:
            # self.video_info_flag = 0
            pass
        
    def extract_video_comments(self):
        CHECK_FLAG = True
        comment_list = []
        try:
            comment_el_list = self.driver.find_elements(by=By.XPATH, value=self.video_comments_xpath)
                          
            actions = ActionChains(self.driver)
            if len(comment_el_list):
                actions.move_to_element(comment_el_list[-1]).perform()
            else:
                CHECK_FLAG = False
                raise Exception
            time.sleep(1)
            self.driver.execute_script("window.scrollBy(0,500)")
            # post_comment_button.click()
            time.sleep(10)
            WAIT_LOOP = 3
            while len(comment_el_list) == self.comment_el_len and WAIT_LOOP:
                comment_el_list = self.driver.find_elements(by=By.XPATH, value=self.video_comments_xpath)
                WAIT_LOOP -= 1
                print(WAIT_LOOP)
                time.sleep(15)
            if not WAIT_LOOP:
                logger.critical(f'Fail to get the comments {self.uuid} comments, crawling comments exit anomally!')
                CHECK_FLAG = False
                raise Exception 
            print(self.element_index)
            for id in range(len(comment_el_list)):
                if id <= self.element_index:
                    continue
                else:
                    self.element_index = id
                comment = YtComment() 
                author = comment_el_list[id].find_element(by=By.XPATH, value=self.comment_author_xpath).text

                publish_time_str = comment_el_list[id].find_element(by=By.XPATH, value=self.comment_publish_time_xpath).text
                content = comment_el_list[id].find_element(by=By.XPATH, value=self.comment_content_xpath).text
                up_num = comment_el_list[id].find_element(by=By.XPATH, value=self.comment_up_num_xpath).text
                try:
                    retweet_el = comment_el_list[id].find_element(by=By.XPATH, value=self.comment_retweet_num_xpath)
                    # print(retweet_num_str)
                    retweet_num_str = retweet_el.getattribute('aria-label')
                except NoSuchElementException:                
                    retweet_num_str = ''
                comment.author = author
                # comment_dict['author_thumbnail'] = author_img_url
                comment.publish_time = datetime_util.parse_yt_time(publish_time_str, self.extract_time)        
                comment.extract_time =  self.extract_time.strftime(r'%Y-%m-%d')      
                comment.content= content    
                comment.uuid = util.gen_uuid(content)       
                comment.post_uuid = self.uuid 
                comment.up_num = util.parse_number(up_num)                  
                comment.retweet_num = util.parse_number(retweet_num_str.split()[0]) if retweet_num_str else 0       
                print(comment.__dict__)        
                comment_list.append(comment)
            self.comment_el_len = len(comment_el_list)
            print(len(comment_list))
        except NoSuchElementException as e:
            CHECK_FLAG = False
            logger.exception(e)
            logger.warning('extracting post comment finished!')
        except Exception as e:
            CHECK_FLAG = False
            logger.exception(e)
            logger.warning('extracting post comment failed!') 
        finally: 
            return comment_list, CHECK_FLAG

    def extract_video_posts(self, account):
        return True
    
    def extract_account_posts(self, account, config):
        CHECK_DATE = True
        CHECK_FLAG = False
        INFO_FLAG = False
        post_list = []
        comment_list = []
        try:
            video_info, INFO_FLAG = self.extract_video_info() if self.video_info_flag else (None, True)
            self.video_info_flag = 0
            if not INFO_FLAG:
                raise Exception
            if video_info:
                post_list.append(video_info)
            
            # CHECH_DATE = self.extract_video_posts(account)
            comment_list, CHECK_FLAG = self.extract_video_comments() 
        except Exception as e:
            logger.exception(e)
        finally:       
            return post_list, comment_list, CHECK_DATE, CHECK_FLAG
    
    
        
    




    
