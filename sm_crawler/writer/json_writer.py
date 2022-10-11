import logging
import json,os
from .writer import Writer

logger = logging.getLogger('crawler.json_writer')

from .writer import Writer 
class JsonWriter(Writer):
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        
    def write_posts(self, file_name, posts):
        """将爬取的post写入json文件，以account为单位"""
        try:
            if not os.path.exists('/code/sm_crawler/data/json/'):
                os.makedirs('/code/sm_crawler/data/json/')
        except Exception as e:
            logger.critical('Create json dir failed!') 
            return
        with open(self.json_file_path+file_name+'_post.json', 'a', newline='\n', encoding='utf-8') as f:        
            for post in posts:
                f.write(json.dumps(post.__dict__, ensure_ascii=False)+'\n')       
        logger.info(f'%d posts has written to json file.', len(posts))

    def write_comments(self, file_name, comments):
        """将爬取的post写入json文件，以account为单位"""
        with open(self.json_file_path+file_name+'_comment.json', 'a', newline='\n', encoding='utf-8') as f:        
            for post in comments:
                f.write(json.dumps(post.__dict__, ensure_ascii=False)+'\n')       
        logger.info(f'%d comments has written to json file.', len(comments))

    def write_account(self, account):
        pass