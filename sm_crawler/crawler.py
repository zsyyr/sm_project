import logging
import logging.config
import os
from tabnanny import check
import yaml

import config_parser 
import extractor.fb_extractor as fb_extractor
import extractor.tw_extractor as tw_extractor
import extractor.wb_extractor as wb_extractor
import datetime_util
import account.account as account
import writer.json_writer as json_writer
import writer.mongo_writer as mongo_writer
from driver import chrome_driver


try:
    if not os.path.exists('/code/sm_crawler/log/'):
        os.makedirs('/code/sm_crawler/log/')
    logging_path = '/code/sm_crawler/logconf.yml'
    with open(logging_path, "r", encoding='utf-8') as f:
        dict_conf = yaml.safe_load(f)
    logging.config.dictConfig(dict_conf)
    logger = logging.getLogger('crwaler')
except Exception as e:
    print(e)
    


class Crawler:
    def __init__(self, config):
        self.config = config
        self.account_list = []
        self.remote_driver_flag = config_parser.get_remote_driver_flag(self.config)
        self.remote_driver_selenium_grid_url = config_parser.get_remote_driver_selenium_grid_url(self.config)
        self.remote_debugger_flag = config_parser.get_remote_debugger_flag(self.config)
        self.remote_debugger_address = config_parser.get_remote_debugger_address(self.config)
        self.authorization_flag = config_parser.get_authorization_config(self.config)
        self.start_hour = config_parser.get_everyday_starthour(self.config)
        self.stop_date = config_parser.get_stop_date(self.config)
        self.global_wait_seconds_scale = config_parser.get_global_wait_scale(self.config)
        self.global_wait_threshold = config_parser.get_global_wait_threshold(self.config)
        self.random_wait_seconds_scale = config_parser.get_random_wait_scale(self.config)
        self.mongodb_config = config_parser.get_mongo_config(self.config)
        self.web_driver_path = config_parser.get_webdriver_path(self.config, 'chrome')
        self.implicitly_wait_second = config_parser.get_implicitly_wait_second(self.config)
        self.comment_threshold = config_parser.get_comment_threshold(self.config)
        self.comment_max_num = config_parser.get_comment_max_count(self.config)
        self.webdriver = None
        self.extractor = None
        self.json_file_path = ''
        self.writers = []
        self.total_crawling_post_number = 0
        self.scroll_detect_wait_time = config_parser.get_scroll_detect_wait_time(self.config)
    
    def write_post(self, posts, account_name):
        for writer in self.writers:
            writer.write_posts(posts, account_name)
        
    def write_comments(self, posts, account_name):
        for writer in self.writers:
            writer.write_comments(posts, account_name)    

    def init_accounts(self):
        if self.config:
            single_task = self.config['single_task_config']
            task_accounts = single_task['accounts']
            if single_task['flag']:
                for st_account in single_task['accounts']:
                    sm_account = account.Account(task_accounts[st_account]['name'], 
                                                 task_accounts[st_account]['platform'], 
                                                 task_accounts[st_account]['url'],
                                                 task_accounts[st_account]['stop_date'])
                    self.account_list.append(sm_account)
            else:
                for platform in self.config['platforms']:
                    if self.config[platform]['accounts']:
                        for account_config_name in self.config[platform]['accounts']:                            
                            sm_account = account.Account(account_config_name, 
                                                         platform, 
                                                         self.config[platform]['url']+account_config_name, 
                                                         self.stop_date)
                            self.account_list.append(sm_account)
        [print(sm_account.url) for sm_account in self.account_list]

    def init_driver(self):
        self.webdriver = chrome_driver.ChromeWebDriver()
        if self.remote_driver_flag:
            self.webdriver.driver = self.webdriver.get_selenium_grid_driver(self.remote_driver_selenium_grid_url)
        else:
            if self.remote_debugger_flag:
                self.webdriver.remote_options_config(self.remote_debugger_address)
            else:
                self.webdriver.options_config()
            self.webdriver.web_driver_path = self.web_driver_path
            self.webdriver.service_config()

    def init_writers(self):       
        if self.config['json_store']['flag']:
            self.json_file_path = config_parser.get_json_file_path(self.config)
            self.writers.append(json_writer.JsonWriter(self.json_file_path))
        if self.config['db_store']['mongo_db']['flag']:
            self.writers.append(mongo_writer.MongoWriter(self.config['db_store']['mongo_db']['connection_string']))   

    def open_url(self, website_url):
        if self.authorization_flag:
            self.webdriver.open_tab_by_url(website_url, self.implicitly_wait_second)
        else:
            self.webdriver.open_tab_by_url_with_cookies(website_url, self.implicitly_wait_second)

    def check_posts_content(self, post_list):
        return [post.content for post in post_list]

    def get_one_account_posts(self, account):
        DATE_CHECK = True
        WAIT_CHECK = True
        self.extractor.element_index = -1
        logger.info(f"Begin to crawl account {account.name}")
        while True:
            post_list = []
            post_list, comment_list, DATE_CHECK, WAIT_CHECK = self.extractor.extract_account_posts(account, 
                                                                                   self.global_wait_threshold, 
                                                                                   self.global_wait_seconds_scale,
                                                                                   self.comment_threshold,
                                                                                   self.comment_max_num,
                                                                                   self.scroll_detect_wait_time)
            if not self.check_posts_content(post_list):
                logger.critical('Post content crawling failed, crawling stopped anomally!')
                break
            self.write_post(account.platform, post_list) 
            self.write_comments(account.platform, comment_list)             
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
            if account.platform == 'Twitter':
                self.extractor = tw_extractor.TwExtractor(self.webdriver.driver)
            if account.platform == 'Weibo':                
                self.extractor = wb_extractor.WbExtractor(self.webdriver.driver)
            
            account.start_time = datetime_util.get_now_time()
            self.open_url(account.url)
            self.get_one_account_posts(account)
            
    def end(self):
        total_posts_number = self.get_crawling_post_number()
        logger.info(f'Totally crawling posts {total_posts_number}')
        self.webdriver.close_driver()

def main():
    try:
        config = config_parser.get_yaml_config()
        crawler = Crawler(config)
        logger.info('Start crawler procedure.')        
        crawler.start() 
        crawler.end() 
    except Exception as e:
        logger.exception(e)


if __name__ == '__main__':
    main()














