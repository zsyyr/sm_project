import yaml
import logging
import os
import sys
from datetime import datetime
from account.account import Account

logger = logging.getLogger('crawler.config_parser')

YAML_CONFIG_FILE = "crawler_conf.yml"

class PlatformInfo:
    def __init__(self, platform, platform_info_dict):
        self.name = platform 
        self.sm_account_email = platform_info_dict['sm_account_email']
        self.password = platform_info_dict['password']
        self.cookies_file = platform_info_dict['cookies_file']
        self.account_list = platform_info_dict['accounts']
        self.url = platform_info_dict['url']


class CrawlingConfig:
    def __init__(self, crawling_mode, task_mode, auth_mode, path_prefix):
        self.crawling_mode = crawling_mode
        self.task_mode = task_mode
        self.auth_mode = auth_mode
        self.path_prefix = path_prefix        
        self.config_dict = self.get_yaml_config_dict(self.path_prefix + YAML_CONFIG_FILE)
        
        self.remote_debugger_address = self.get_remote_debugger_address()
        self.web_browser = self.get_web_browser()
        self.webdriver_path = self.get_webdriver_tool_path(self.web_browser)
        self.remote_driver_selenium_grid_url = self.get_remote_driver_selenium_grid_url()
        
        self.platform_info_list = self.get_platform_info_list()
        self.stop_date = self.get_stop_date()
        self.daily_task_account_list = self.get_daily_task_account_list()
        self.daily_start_hour = self.get_daily_start_hour()
        self.single_task_dict = self.get_single_task_dict()
        self.single_task_account_list = self.get_single_taskt_account_list()
        
        self.comment_threshold = self.get_comment_threshold()
        self.comment_max_count = self.get_comment_max_count()
        
        self.global_wait_threshold = self.get_global_wait_threshold()
        self.global_wait_scale = self.get_global_wait_scale()
        self.random_wait_scale = self.get_random_wait_scale()
        self.implicitly_wait_second = self.get_implicitly_wait_second()
        self.scroll_detect_wait_time = self.get_scroll_detect_wait_time()
        
        self.json_store_flag = self.get_json_store_flag()
        self.json_file_path = self.get_json_file_path()
        self.mongo_store_flag = self.get_mongo_store_flag()   
        self.mongo_connection_string = self.get_mongo_connection_string()     
        
        # self.authorization_mode_dict = self.get_authorization_mode_dict()
     
        
        
    def get_yaml_config_dict(self, yaml_file):
        logger.info("Parsing config yaml data.")
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data_dict = yaml.load(f, Loader=yaml.FullLoader)
        return data_dict
            
    def get_platform_info_list(self):
        return [PlatformInfo(platform, self.config_dict[platform]) for platform in self.config_dict['platform_list']]
  
    def get_remote_driver_flag(self):
        return self.config_dict['remote_driver']['flag']

    def get_remote_driver_selenium_grid_url(self):
        return self.config_dict['remote_driver']['selenium_grid_url']

    def get_remote_debugger_flag(self):
        return self.config_dict['remote_debugger']['flag']

    def get_remote_debugger_address(self):
        return self.config_dict['remote_debugger']['address']

    def get_daily_task_account_list(self):
            account_info_list = []
            for platform in self.platform_info_list:                
                for config_account in platform.account_list:
                    account = Account(config_account, 
                                      platform.name, 
                                      platform.url+config_account, 
                                      self.stop_date)
                    account_info_list.append(account)
            return account_info_list

    def get_daily_start_hour(self):
        return self.config_dict['daily_start_hour']

    def get_global_wait_threshold(self):
        return self.config_dict['wait_config']['global_wait_seconds']['threshold']

    def get_global_wait_scale(self):
        return self.config_dict['wait_config']['global_wait_seconds']['wait_seconds_scale']

    def get_random_wait_scale(self):
        return self.config_dict['wait_config']['random_wait_seconds_scale']

    def get_web_browser(self):
        return self.config_dict['web_browser']

    def get_webdriver_tool_path(self, browser):
        return self.config_dict['webdriver_tool_path'][browser]

    def get_stop_date(self):
        return self.config_dict['stop_date']
    
    def get_json_store_flag(self):
        return self.config_dict['json_store']['flag']

    def get_json_file_path(self):
        return self.path_prefix + self.config_dict['json_store']['path']
    
    def get_mongo_store_flag(self):
        return self.config_dict['db_store']['mongo_db']['flag']
    
    def get_mongo_connection_string(self):
        return self.config_dict['db_store']['mongo_db']['connection_string'][self.crawling_mode]

    def get_implicitly_wait_second(self):
        return self.config_dict['implicitly_wait_second']

    def get_scroll_detect_wait_time(self):
        return self.config_dict['scroll_detect_wait_time']

    def get_comment_threshold(self):
        return self.config_dict['comment_config']['threshold']

    def get_comment_max_count(self):
        return self.config_dict['comment_config']['max_count']

    def get_authorization_mode_dict(self):
        return self.config_dict['authorization']

    def get_auto_authorization_flag(self):
        return self.config_dict['authorization']['browser_auto']

    def get_email_authorization_flag(self):
        return self.config_dict['authorization']['email_pwd']

    def get_cookies_authorization_flag(self):
        return self.config_dict['authorization']['cookies']

    def get_sm_account_email_password(self,platform):
        return {'email':self.config_dict[platform]['sm_account_email'], 'pwd':self.config_dict[platform]['password']}

    def get_single_task_dict(self):
        return self.config_dict['single_task_config']['accounts']

    def get_single_taskt_account_list(self):
        single_task_account_list = []
        for key in self.single_task_dict:
            single_taskt_account = Account(
                self.single_task_dict[key]['name'],
                self.single_task_dict[key]['platform'],
                self.single_task_dict[key]['url'],
                self.single_task_dict[key]['stop_date'],
                self.single_task_dict[key]['crawling_comment_flag']
            )
            single_task_account_list.append(single_taskt_account)
        return single_task_account_list

if __name__ == '__main__':
    
    config = CrawlingConfig('browser_debug', 
                            'daily_task', 
                            'browser_auto', 
                            '/home/zsyyr/sm_project/sm_crawler/')
    # print(config)
    # plateforms = config['platforms']
    # print(plateforms)
    # # url = [config[platform]['url'] + config[platform][account] for account in config[platform]['accounts'] for platform in config['platform']]
    # print(get_everyday_starthour(config))
    # # print(url)
    # print(get_global_wait_scale(config)[0])
    # print(get_global_wait_threshold(config))
    # print(get_random_wait_scale(config))
    # print(get_mongo_config(config))
    # print(config.__dict__)
    # print(config.single_task_dict)
    # config.get_single_account_list()
    # print(config.single_task_account_list)
    # print(config.platform_list)
    # [print(platform_info.__dict__) for platform_info in config.platform_info_list]
    # [print(account_info.__dict__) for account_info in config.daily_task_account_list]
    # [print(account.__dict__) for account in config.single_task_account_list]
    print(config.get_single_task_dict())
