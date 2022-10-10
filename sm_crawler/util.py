from curses.ascii import isdigit
import json
import io
import csv
import uuid
import random
import string
import logging
import re

logger = logging.getLogger('crwaler.util')

class Singleton(object):
    def __init__(self, cls):
        self._cls = cls
        self._instance = {}
    def __call__(self):
        if self._cls not in self._instance:
            self._instance[self._cls] = self._cls()
        return self._instance[self._cls]


def dump_comment_2csv(filename, comments):
    with io.open(filename, 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow("Comment")
        for comment in comments:
            writer.writerow([comment])

def dump_comment_2json(filename, comments):    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(comments, f, ensure_ascii=False)

def gen_uuid(uuid_str):
    return uuid.uuid3(uuid.NAMESPACE_OID, uuid_str[:8]) \
                    if len(uuid_str)>8 else uuid.uuid3(uuid.NAMESPACE_OID, uuid_str)


def parse_number(str_number):
    number = 0    
    try:
        if ',' in str_number:
            number = float(str_number.replace(',', ''))
        else:        
            if str_number[-1] == 'k' or str_number[-1] == 'K':
                number = float(str_number[:-1])*1000
            else:
                if str_number[-1] == 'm' or str_number[-1] == 'M':
                    number = float(str_number[:-1])*10000
                else:
                    number = float(str_number)
    except:        
        if str_number:
            print("Get number false: %s" % str_number)
        return 0
    else:
        return number
 
def get_retweet_comment_str(number_str):
    try:
        return number_str.split(' ')[0]
    except:
        return ''
    
def get_up_str(number_str):
    try:
        str_list = number_str.split(' ')
        str_len = len(str_list)
        if str_len == 1:
            return number_str
        else:
            return str_list[-2]
    except:
        return ''

def get_rand_char(n):    
    return ''.join(random.sample(string.ascii_letters + string.digits, n))

def parse_post_comment_str(comment):       
    str_list = comment.raw_str.strip().split('\n')
    content_end_index = 0
    up_index = 0
    like_index = 0
    try:
        comment.author = str_list[0]
        for i,s in enumerate(str_list):
            up_number = re.findall('^\d$', s)
            if up_number:
                comment.up_num = up_number[0]
                up_index = i
            
            like_str = re.findall('^Like$', s)
            if like_str:
                like_index = i
                
            time_str = re.findall('^Reply.*?(\d [s,m,h,d]).*?$', s)  
            if time_str:
                comment.publish_time = time_str[0]
            
            retweet_num = re.findall('^.*?(\d) repl.*?$', s)
            if retweet_num:
                comment.retweet_num = retweet_num[0]
        content_end_index = up_index if up_index else like_index
        comment.content = ". ".join(str_list[1:content_end_index])
    except Exception as e:
        logger.debug(e)        
