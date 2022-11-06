from datetime import datetime, date, time, timedelta
import calendar
import logging
import time
import random

logger = logging.getLogger('crwaler.datetime_util')

def str_to_time(text):
    """将字符串转换成时间类型"""
    if ':' in text:
        result = datetime.strptime(text, '%Y-%m-%d %H:%M')
    else:
        result = datetime.strptime(text, '%Y-%m-%d')
    return result

def get_datetime(time_tuple,date_interval=None):
    _datetime = None
    _date = date.today() if not date_interval \
        else date.today() + timedelta(days=date_interval)
    
    _time = time(hour=time_tuple.hour, minute=time_tuple.minute, \
        second=time_tuple.second) if time_tuple else None
    try:
        _datetime = datetime.combine(_date, _time)
    except:
        _datetime = None
    return _datetime


def get_now_time():
    return datetime.now()

def time_miner_seconds(current_time, start_time):
    return (current_time-start_time).seconds

def check_date(post_date_str, account):
    try:
        time_miner = (datetime.now() - datetime.fromisoformat(post_date_str)).days 
        if time_miner < 1:
            today = 1  
        else:
            today = 0     
        return time_miner < int(account.stop_date), today
    except Exception as e:
        logger.error(e)
        return True, 1

# TODO:fix time zone
def parse_tz():
    pass


def parse_tw_time(time_str, crawling_date):
    '''
    2022-11-01T11:31:14.000Z
    '''
    try:
        return time_str.split('T')[0]
    except:
        return ''
        


def parse_time(time_str, crawling_date):    
    '''
    crawl_date_str: "2022-03-23 14:05:00" '%Y-%m-%d %H:%M:%S'
    raw_date:       "23 March at 14:05"
    raw_date:       ["23 h/23h", "just now"]
    ''' 
    crawl_year = str(crawling_date.year)
    try:
        s_list = time_str.split()
        l = len(s_list)    
        if 'now' in time_str.lower():
            return crawling_date.strftime(r'%Y-%m-%d') 
    
        if l==1 and time_str[-1]=='s':    
            delta = timedelta(seconds=int(time_str[:-1]))      
            n_days = crawling_date - delta      
            return n_days.strftime(r'%Y-%m-%d') 
        if l==1 and time_str[-1]=='m':    
            delta = timedelta(minutes=int(time_str[:-1]))      
            n_days = crawling_date - delta      
            return n_days.strftime(r'%Y-%m-%d') 
        if l==1 and time_str[-1]=='h':
            delta = timedelta(hours=int(time_str[:-1]))    
            n_days = crawling_date - delta      
            return n_days.strftime(r'%Y-%m-%d')  
        if l==1 and time_str[-1]=='d':
            delta = timedelta(hours=int(time_str[:-1])*24)      
            n_days = crawling_date - delta      
            return n_days.strftime(r'%Y-%m-%d') 
            
        day = s_list[0]   
        if len(day) ==1:
            day = '0' + day        
        if l==2 and s_list[-1]=='s':    
            delta = timedelta(seconds=int(s_list[0]))      
            n_days = crawling_date - delta      
            return n_days.strftime(r'%Y-%m-%d') 
        if l==2 and s_list[-1]=='m':    
            delta = timedelta(minutes=int(s_list[0]))      
            n_days = crawling_date - delta      
            return n_days.strftime(r'%Y-%m-%d') 
        if l==2 and s_list[-1]=='h':
            delta = timedelta(hours=int(s_list[0]))      
            n_days = crawling_date - delta   
            return n_days.strftime(r'%Y-%m-%d')  
        if l==2 and s_list[-1]=='d':
            delta = timedelta(hours=int(s_list[0])*24)      
            n_days = crawling_date - delta      
            return n_days.strftime(r'%Y-%m-%d') 
        if l==2 and len(s_list[-1])>1:
            month = str(list(calendar.month_name).index(s_list[1])) 
            if len(month)==1:
                month = '0' + month     
            year = crawl_year           
            return "-".join([year,month,day])
        if l==3:
            month = str(list(calendar.month_name).index(s_list[1]))      
            if len(month)==1:
                month = '0' + month 
            year = s_list[2]                     
            return "-".join([year,month,day])             
        if l==4:
            month = str(list(calendar.month_name).index(s_list[1]))
            if len(month)==1:
                month = '0' + month 
            year = crawl_year
            hm = s_list[3].split(':')
            return "-".join([year,month,day])
    except Exception as e:
        logging.exception(e)
        return ''

def parse_yt_time(time_str, crawling_date):    
    '''
    TODO: year month
    '''
    crawl_year = str(crawling_date.year)
    try:
        s_list = time_str.split()
        # print(s_list)    
        if time_str == "just now":
            return crawling_date.strftime(r'%Y-%m-%d') 
        if 'second' in s_list[1]:    
            delta = timedelta(seconds=int(s_list[0]))      
            n_days = crawling_date - delta      
            return n_days.strftime(r'%Y-%m-%d') 
        if 'minute' in s_list[1]:    
            delta = timedelta(minutes=int(s_list[0]))      
            n_days = crawling_date - delta      
            return n_days.strftime(r'%Y-%m-%d') 
        if 'hour' in s_list[1]:    
            delta = timedelta(hours=int(s_list[0]))      
            n_days = crawling_date - delta      
            return n_days.strftime(r'%Y-%m-%d') 
        if 'day' in s_list[1]:    
            delta = timedelta(hours=int(s_list[0])*24)      
            n_days = crawling_date - delta      
            return n_days.strftime(r'%Y-%m-%d')   
    except Exception as e:
        logging.exception(e)
        return ''

def global_wait(account, global_wait_threshold, wait_seconds_scale):      
    if time_miner_seconds(datetime.now(), account.start_time) > global_wait_threshold:
        sleep_time = random.randint(wait_seconds_scale[0], wait_seconds_scale[1])
        logger.info(f'Runing time lasted more than 30 minutes, sleep for {sleep_time} seconds.')
        time.sleep(sleep_time)
        account.start_time = datetime.now()