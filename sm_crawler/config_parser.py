import yaml
import logging
import os
import sys
from datetime import datetime

logger = logging.getLogger('crawler.config_parser')

YAML_CONFIG = "crawler_conf.yml"

def get_yaml_config_data(yaml_file):
    logger.info("Getting config yaml data.")
    with open(yaml_file, 'r', encoding='utf-8') as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    return data

def get_yaml_path(yaml_file):
    current_path = os.path.abspath(".")
    return os.path.join(current_path, yaml_file)

def get_yaml_config():
    return get_yaml_config_data('/code/sm_crawler/crawler_conf.yml')

def get_remote_driver_flag(config):
    return config['remote_driver']['flag']

def get_remote_driver_selenium_grid_url(config):
    return config['remote_driver']['selenium_grid_url']

def get_remote_debugger_flag(config):
    return config['remote_debugger']['flag']

def get_remote_debugger_address(config):
    return config['remote_debugger']['address']

def get_account_urls(config):
        account_urls = []
        for platform in config['platforms']:
            account_url_list = [config[platform]['url'] + account for account in config[platform]['accounts']]
            account_urls.extend(account_url_list)
        return account_urls

def get_everyday_starthour(config):
    return config['everyday_start_hour']

def get_global_wait_threshold(config):
    return config['wait_config']['global_wait_seconds']['threshold']

def get_global_wait_scale(config):
    return config['wait_config']['global_wait_seconds']['wait_seconds_scale']

def get_random_wait_scale(config):
    return config['wait_config']['random_wait_seconds_scale']

def get_mongo_config(config):
    return config['db_store']['mongo_db']

def get_webdriver_path(config, webdriver):
    return config['webdriver_tool_path'][webdriver]

def get_stop_date(config):
    return config['stop_date']

def get_json_file_path(config):
    return config['json_store']['path']

def get_implicitly_wait_second(config):
    return config['implicitly_wait_second']

def get_scroll_detect_wait_time(config):
    return config['scroll_detect_wait_time']

def get_comment_threshold(config):
    return config['comment_config']['threshold']

def get_comment_max_count(config):
    return config['comment_config']['max_count']

def get_authorization_config(config):
    return config['authorization']['browser_auto_auth']

if __name__ == '__main__':
    
    config = get_yaml_config()
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
    print(get_webdriver_path(config, 'chrome'))
