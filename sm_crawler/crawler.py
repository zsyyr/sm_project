import logging
import logging.config
import sys
import extractor.fb_extractor as fb_extractor
import extractor.tw_extractor as tw_extractor
import extractor.yt_extractor as yt_extractor
import extractor.wb_extractor as wb_extractor
import datetime_util
import account.account as account
import writer.json_writer as json_writer
import writer.mongo_writer as mongo_writer
from driver import chrome_driver
import crawler_exception as ce


logger = logging.getLogger('crawler.crawler')    


class Crawler:
    def __init__(self, config):
        self.config = config   
        self.account_list = []          
        self.webdriver = None
        self.extractor = None        
        self.writers = []
        self.total_crawling_post_number = 0   
    
    def write_post(self, posts, account_name):
        for writer in self.writers:
            writer.write_posts(posts, account_name)
        
    def write_comments(self, posts, account_name):
        for writer in self.writers:
            writer.write_comments(posts, account_name)    
    
    def init_accounts(self):
        try:
            if self.config.task_mode == 'single_task':
                self.account_list = self.config.single_task_account_list
            elif self.config.task_mode == 'daily_task':
                self.account_list = self.config.daily_task_account_list
            [logger.info(sm_account.url) for sm_account in self.account_list]
        except Exception as e:
            logger.exception(e)
            raise ce.ConfigException

    def init_driver(self):
        self.webdriver = chrome_driver.ChromeWebDriver()
        if self.config.crawling_mode == 'selenium_grid_docker':
            self.webdriver.driver = self.webdriver.get_selenium_grid_driver(self.config.remote_driver_selenium_grid_url)
        else:
            if self.config.crawling_mode == 'browser_debug' or self.config.crawling_mode == 'browser_debug_docker':
                self.webdriver.remote_options_config(self.config.remote_debugger_address)
            else:
                self.webdriver.options_config()
            self.webdriver.web_driver_path = self.config.path_prefix + self.config.webdriver_path
            self.webdriver.service_config()

    def init_writers(self):
        try:       
            if self.config.json_store_flag:            
                self.writers.append(json_writer.JsonWriter(self.config.json_file_path))
            if self.config.mongo_store_flag:
                self.writers.append(mongo_writer.MongoWriter(self.config.mongo_connection_string))   
        except ce.StoreException as e:
            logger.exception(e)
            raise ce.LoginException
        except Exception as e:
            logger.exception(e)
            raise Exception

    def open_url(self, account):
        try:
            if self.config.auth_mode == 'browser_auto':
                self.webdriver.open_tab_by_url(account.url, self.config.implicitly_wait_second)
            elif self.config.auth_mode == 'email_pwd':
                self.sm_account = self.config.get_sm_account_email_password(account.platform)
                self.webdriver.open_tab_by_url(account.url, self.config.implicitly_wait_second)
                self.webdriver.login_with_email_pwd(self.sm_account)
            elif self.config.auth_mode == 'cookies':
                self.webdriver.open_tab_by_url_with_cookies(account.url, self.config.implicitly_wait_second)
        except ce.LoginException as e:
            logger.exception(e)
            raise ce.LoginException
        except Exception as e:
            logger.exception(e)
            raise Exception
            
    def check_posts_content(self, post_list):
        return [post.content for post in post_list]
    
    def check_comment_content(self, comment_list):
        return [comment.content for comment in comment_list]    

    def get_one_account_posts(self, account):
        DATE_CHECK = True
        WAIT_CHECK = True
        self.extractor.element_index = -1
        logger.info(f"Begin to crawl account {account.name}")
        while True:
            post_list = []
            post_list, comment_list, DATE_CHECK, WAIT_CHECK = self.extractor.extract_account_posts(account, self.config)
            # TODO: single task as YouTube comment without posts
            # if not self.check_posts_content(post_list) or not self.check_comment_content(comment_list):
            #     logger.critical('Post content crawling failed, crawling stopped anomally!')
            #     break
            if post_list:
                self.write_post(account, post_list) 
            if comment_list:
                self.write_comments(account, comment_list)             
            account.crawling_post_number += len(post_list) 
             
            if not DATE_CHECK:
                logger.info("Date check has matched the stop date, crawling finished!")
                break
            if not WAIT_CHECK:
                logger.critical('Account crawling stopped for web connecting offline!')
                break                                
        logger.info(f"End to crawl account {account.name}, crawling {account.crawling_post_number} posts")

    def get_crawling_post_number(self):
        posts_number = 0
        for account in self.account_list:
            posts_number += account.crawling_post_number 
        return posts_number
    
    def start(self):
        self.init_accounts()
        self.init_driver()
        self.init_writers()
        for account in self.account_list:
            if account.platform == 'FB':
                self.extractor = fb_extractor.FbExtractor(self.webdriver.driver)                
            if account.platform == 'TW':
                self.extractor = tw_extractor.TwExtractor(self.webdriver.driver)
            if account.platform == 'YT':                
                self.extractor = yt_extractor.YtExtractor(self.webdriver.driver)
            if account.platform == 'WB':                
                self.extractor = wb_extractor.WbExtractor(self.webdriver.driver)
            account.start_time = datetime_util.get_now_time()
            self.open_url(account)
            self.get_one_account_posts(account)
            
    def end(self):
        total_posts_number = self.get_crawling_post_number()
        logger.info(f'Totally crawling posts {total_posts_number}')
        self.webdriver.close_driver()

def main(config):
    try:
        crawler = Crawler(config)
        logger.info('Start crawler procedure.')        
        crawler.start() 
        crawler.end() 
    except ce.ConfigException as e:
        logger.exception(e)
        sys.exit()
    except ce.LoginException as e:
        logger.exception(e)
        sys.exit()
    except ce.StoreException as e:
        logger.exception(e)
        sys.exit()
    except Exception as e:
        logger.exception(e)
        sys.exit()


if __name__ == '__main__':
    main()

