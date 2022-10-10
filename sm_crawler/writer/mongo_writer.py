import copy
import logging
import sys
import pymongo
from .writer import Writer

logger = logging.getLogger('crawler.mongo_writer')

class MongoWriter(Writer):
    def __init__(self, connection_str):
        self.mongo_config = None
        self.connection_string = connection_str
        self.client = self.mongodb_connect()
        self.db_today = self.client['today']
        self.db_yesterday = self.client['yesterday']
        self.db_comment = self.client['comment']
        
    def mongodb_connect(self):
        try:
            client = pymongo.MongoClient(self.connection_string)
            client['admin'].authenticate('root', 'root')
            return client
        except pymongo.errors.OperationFailure as e:
            logger.exception(e)
        except pymongo.errors.ServerSelectionTimeoutError:
            logger.warning(
                u'系统中可能没有安装或启动MongoDB数据库，请先根据系统环境安装或启动MongoDB，再运行程序')
            sys.exit()

    def close_mongodb(self):
        self.client.close()

    def _post_to_mongodb(self, collection_name, post_list):
        """将爬取的信息写入MongoDB数据库"""        
        try:   
            new_post_list = copy.deepcopy(post_list)
            for post in new_post_list:
                if post['today_flag']:
                    db = self.db_today
                else:
                    db = self.db_yesterday
                collection = db[collection_name+'_'+post['type']]
                if not collection.find_one({'id': post['uuid']}):
                    collection.insert_one(post)
                else:
                    collection.update_one({'id': post['uuid']}, {'$set': post})
        except pymongo.errors.ServerSelectionTimeoutError:
            logger.warning(
                u'系统中可能没有安装或启动MongoDB数据库，请先根据系统环境安装或启动MongoDB，再运行程序')
            sys.exit()
    def _comment_to_mongodb(self, collection_name, post_list):
        """将爬取的信息写入MongoDB数据库"""        
        try:   
            new_post_list = copy.deepcopy(post_list)
            for post in new_post_list:
                db = self.db_comment
                collection = db[collection_name+'_'+post['type']]
                if not collection.find_one({'id': post['uuid']}):
                    collection.insert_one(post)
                else:
                    collection.update_one({'id': post['uuid']}, {'$set': post})
        except pymongo.errors.ServerSelectionTimeoutError:
            logger.warning(
                u'系统中可能没有安装或启动MongoDB数据库，请先根据系统环境安装或启动MongoDB，再运行程序')
            sys.exit()
            
    def write_posts(self,collection, posts):
        """将爬取的信息写入MongoDB数据库"""
        post_list = []
        for w in posts:
            post_list.append(w.__dict__)
        self._post_to_mongodb(collection, post_list)
        logger.info(u'%d posts has written to Mongodb.', len(posts))
 
    def write_comments(self,collection, comments):
        """将爬取的信息写入MongoDB数据库"""
        post_list = []
        for w in comments:
            post_list.append(w.__dict__)
        self._comment_to_mongodb(collection, post_list)
        logger.info(u'%d comments has written to Mongodb.', len(comments))
 
    def write_account(self, account):
        """将爬取的用户信息写入MongoDB数据库"""
        self.user = account
        user_list = [account.__dict__]
        self._post_to_mongodb('account', user_list)
        logger.info(u'account %s has written to Mongodb.', account.nickname)
