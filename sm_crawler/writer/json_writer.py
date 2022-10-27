import logging
import json,re
from .writer import Writer

logger = logging.getLogger('crawler.json_writer')

from .writer import Writer 
class JsonWriter(Writer):
    def __init__(self, json_file_path):
        self.json_file_path = json_file_path
        
    def write_posts(self, account, posts):
        """将爬取的post写入json文件，以account为单位"""
       
        strinfo = re.compile(r'[/:*?"<>|\\]')  
        name = strinfo.sub('_', account.name)
        with open(self.json_file_path+account.platform+'_'+name+'_post.json', 'a', newline='\n', encoding='utf-8') as f:        
            for post in posts:
                f.write(json.dumps(post.__dict__, ensure_ascii=False)+'\n')       
        logger.info(f'%d posts has written to json file.', len(posts))

    def write_comments(self, account, comments):
        """将爬取的post写入json文件，以account为单位"""
        strinfo = re.compile(r'[/:*?"<>|\\]')  
        name = strinfo.sub('_', account.name)
        with open(self.json_file_path+account.platform+'_'+name+'_comment.json', 'a', newline='\n', encoding='utf-8') as f:        
            for comment in comments:
                f.write(json.dumps(comment.__dict__, ensure_ascii=False)+'\n')       
        logger.info(f'%d comments has written to json file.', len(comments))

    def write_account(self, account):
        pass