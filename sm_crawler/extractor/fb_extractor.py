import platform
sys = platform.system()
if sys == 'Linux':
    from socket import TIPC_MEDIUM_IMPORTANCE
    
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException, InvalidSessionIdException
import logging
import datetime, time
import datetime_util
import util
from .extractor import Extractor
from post.fb_post import FbPost
from comment.fb_comment import FbComment

logger = logging.getLogger('crawler.fb_extractor')

class FbExtractor(Extractor):
    def __init__(self, driver): 
        self.driver = driver
        self.page_source = ''         
        self.etree = ''
        self.post_el = None
        self.element_index = 0 
        self.post_failed = 0 # mark whether a post div and its time element is available.
        self.post_list_xpath = '//div[@class="x1t2pt76 x193iq5w xl56j7k x78zum5 x1qjc9v5"]/div/div[@class="xh8yej3"]/div'
        self.post_sibling_el_xpath = './following-sibling::div[1]' 
        self.post_time_el_xpath = './/span[@class="x4k7w5x x1h91t0o x1h9r5lt x1jfb8zj xv2umb2 x1beo9mf xaigb6o x12ejxvf x3igimt xarpa2k xedcshv x1lytzrv x1t2pt76 x7ja8zs x1qrby5j"]/a/span'
        self.post_time_chars_xpath = './/span[@class="x16dsc37 x10wlt62 x6ikm8r x1rg5ohu xt0b8zv"]/span/span'
        self.post_wait_time_hiden_tag_xpath = './/span[@class="x4k7w5x x1h91t0o x1h9r5lt x1jfb8zj xv2umb2 x1beo9mf xaigb6o x12ejxvf x3igimt xarpa2k xedcshv x1lytzrv x1t2pt76 x7ja8zs x1qrby5j"]/a/span/span'
        self.post_time_hiden_tag_xpath = './span'
        
        self.post_content_xpath = './/div[@class="xdj266r x11i5rnm xat24cr x1mh8g0r x1vvkbs x126k92a"]/div'
        self.post_video_src_xpath = './/div[@class="om3e55n1 hf30pyar lq84ybu9"]//video[@class="mfclru0v pytsy3co b6ax4al1"]'
        self.post_pic_description_xpath = './/span[@class=x1lliihq x6ikm8r x10wlt62 x1n2onr6]/span'
        self.post_up_n_xpath = './/span[@class="xt0b8zv x1jx94hy xrbpyxo xl423tq"]/span/span'
        self.post_comment_n_xpath = './/div[@class="x6s0dn4 x78zum5 x2lah0s x17rw0jw"]/div'
        self.post_retweet_n_xpath = ''

        self.comment_button_xpath = './/div[@class="x10wlt62 x6ikm8r x9jhf4c x30kzoy x13lgxp2 x168nmei"]//ul/following-sibling::div'
        self.comment_element_xpath = './/div[@class="x1jx94hy x12nagc"]/ul/li'
        
        
    def extract_post_element_list(self):
        try:
            return self.driver.find_elements(By.XPATH, self.post_list_xpath)
        except Exception as e:
            logger.exception(e)
            return []
    
    def extract_post_time(self, post_el):
        start = time.perf_counter()
        time_chars_el = []
        time_s = ''
        try:
            time_el = post_el.find_element(By.XPATH, self.post_time_el_xpath)
            logger.debug(f'time string: {time_el.text}')
            if time_el: 
                time_chars_el = time_el.find_elements(By.XPATH, self.post_time_chars_xpath)
                if time_chars_el:
                    time_str_list = []
                    for char_el in time_chars_el:
                        if not char_el.get_attribute('style'):
                            time_order = char_el.value_of_css_property('order')
                            time_str_list.append((char_el.text, time_order))
                    time_tuple_list = sorted(time_str_list, key=lambda time_tuple: int(time_tuple[1]))
                    time_s = ''.join([time_tuple[0] for time_tuple in time_tuple_list])
                elif time_el.text:
                    time_s = time_el.text
                if not time_s:
                    time_aria_str_el = time_el.find_element(By.XPATH, self.post_time_hiden_tag_xpath)    
                    time_s = time_aria_str_el.accessible_name
        except NoSuchElementException as e:
            logger.exception(e)
            logger.debug('extracting post time failed!')  
        
        end = time.perf_counter()
        logger.debug(f'runing time of extracting post time : {end-start}')
        return time_s 
    
    def extract_post_content(self, post_el):
        try:
            start = time.perf_counter()
            post_content_el = post_el.find_element(By.XPATH, self.post_content_xpath)
            end = time.perf_counter()
            logger.debug(f'runing time of extracting post content: {end - start}')
            logger.debug(post_content_el)
            return post_content_el.text
        except Exception as e:
            logger.debug('extracting post content failed!')  
            return ''
    
        
    def extract_post_news_description(self, post_el):
        try:            
            start = time.perf_counter()
            post_news_description_el = post_el.find_element(By.XPATH, self.post_pic_description_xpath)
            end = time.perf_counter()
            logger.debug(f'runing time of extracting post news description: {end - start}')
            return post_news_description_el.text
        except Exception as e:
            logger.debug('extracting post news description failed!')  
            return ''
            
    def extract_post_up_number(self, post_el):
        try:
            start = time.perf_counter()
            up_num_el =post_el.find_element(By.XPATH, self.post_up_n_xpath)
            end = time.perf_counter()
            logger.debug(f'runing time of extracting post up number: {end - start}')
            return up_num_el.text
        except Exception as e:
            logger.debug('extracting post up number failed!')  
            return ' '
            
    def extract_post_comment_retweet_number(self, post_el):
        try:
            start = time.perf_counter()
            number_el_list =  post_el.find_elements(By.XPATH, self.post_comment_n_xpath)
            comment_el_n = ''
            retweet_el_n = ''
            el_len = len(number_el_list)
            if el_len == 3:
                comment_el_n = number_el_list[1].text
                retweet_el_n = number_el_list[2].text
            elif el_len == 2:
                el_n = number_el_list[1].text.split(' ')
                if el_n[1] == 'shares':
                    retweet_el_n = el_n[0]                    
                else:
                    comment_el_n = el_n[0]                    
            end = time.perf_counter()
            logger.debug(f'runing time of extracting post comment share number: {end - start}')
            return comment_el_n, retweet_el_n
        except Exception as e:
            logger.debug('Post has no comment and share.')
            return '',''

    def extract_post_comment(self, post_el, post_uuid, comment_max_count):
        post_comment_list = []
        try:
            start = time.perf_counter()
            post_comment_button = post_el.find_element(By.XPATH, self.comment_button_xpath)
            comment_num = 0
            comment_round = 0
            while post_comment_button and comment_num<comment_max_count:                
                actions = ActionChains(self.driver)
                actions.move_to_element(post_comment_button).perform()
                time.sleep(1)
                post_comment_button.click()
                time.sleep(3)
                post_comment_el_list = post_el.find_elements(By.XPATH, self.comment_element_xpath)  
                # fetch 50 next el each time from the post_comment_el li list.
                comment_update_list = post_comment_el_list[50*comment_round:50*(comment_round+1)]
                # check wether the next 50 comment is available, if not, wait for 5s a round within 3 round, then break.
                WAIT_LOOP = 3
                while not len(comment_update_list) and WAIT_LOOP:
                    comment_update_list = post_comment_el_list[50*comment_round:50*(comment_round+1)]
                    WAIT_LOOP -= 1
                    time.sleep(5)
                if not WAIT_LOOP:
                    logger.critical(f'Fail to get the posts {post_uuid} comments, crawling comments exit anomally!')
                    break                    
                start = time.perf_counter()
                for comment_el in comment_update_list:
                    try:
                        if comment_el.text:
                            comment_num += 1
                            comment = FbComment() 
                            comment.post_uuid = post_uuid
                            comment.raw_str = comment_el.text
                            util.parse_post_comment_str(comment)
                            if comment.publish_time:
                                comment.publish_time = datetime_util.parse_time(comment.publish_time)
                            if comment.content:
                                comment.uuid = str(util.gen_uuid(comment.content))
                            else:
                                comment.uuid = str(util.gen_uuid(util.get_rand_char(8)))
                            post_comment_list.append(comment)
                    except Exception as e:
                        logger.warning(f'Parse comment {comment_el.text} failed!')
                        logger.debug(e)
                        
                end = time.perf_counter()
                logger.debug(f'runing time of extracting post comment in round: {end - start}')
                    
                comment_round += 1
                post_comment_button = post_el.find_element(By.XPATH, self.comment_button_xpath)
                # as the comment button xpath exactly choose the ul's sibling div, so when crawl to end, the div selected is not a botton which should be checked by its text content.  
                if '"Most relevant" is selected' in post_comment_button.text:
                    post_comment_button = None
                logger.info(f'crawling {len(post_comment_list)} comments.')
            end = time.perf_counter()
            logger.debug(f'runing time of extracting post comment: {end - start}')
        except NoSuchElementException as e:
            logger.exception(e)
            logger.warning('extracting post comment finished!')
        except Exception as e:
            logger.exception(e)
            logger.warning('extracting post comment failed!') 
        finally: 
            return post_comment_list

    def get_post_el_by_waiting_check(self, post_drive, post_el_xpath, scroll_detect_wait_time):
        SCROLL_DETECT_TIME = 3
        post_el = None
        while SCROLL_DETECT_TIME:
            try:
                post_el = post_drive.find_element(By.XPATH, post_el_xpath) 
                if post_drive != self.driver: # the first post is drived by the post list, only get the first post's div is ok, it's time el has a different mode than other posts. 
                    test_content = post_el.find_element(By.XPATH, self.post_wait_time_hiden_tag_xpath)   # a post's div may be find while it's elements are all unavailable, so must check the post's time element as well.
                self.post_failed = 0
                break                
            except NoSuchElementException:
                logger.warning(f"Waiting:sleep for {scroll_detect_wait_time} seconds waiting for the post loading, detect time is {SCROLL_DETECT_TIME}")
                time.sleep(scroll_detect_wait_time)
                self.post_failed = 1   # if the element is unavailable, mark it and then the account crawling will stop.
            except InvalidSessionIdException:
                self.post_failed = 1
                logger.critical(f'crawling interrupted with a session error!')
            finally:
                SCROLL_DETECT_TIME -= 1
        return post_el                  # maybe a div element or None when the net is unstable.
        

    def extract_account_posts(self, account, global_wait_threshold, global_wait_seconds_scale, comment_threshold, comment_max_count, scroll_detect_wait_time):
        post_list = []
        comment_list = []
        DATE_CHECK = True
        WAIT_CHECK = True
        logger.info('Useing fb extractor, begin to extract posts.') 
        if self.post_el == None:
            self.post_el = self.get_post_el_by_waiting_check(self.driver, self.post_list_xpath, scroll_detect_wait_time)
            if self.post_failed:
                logger.critical('Fail to get the posts, crawling exit anomally!')
                return post_list, comment_list, DATE_CHECK, False
                
        while True:
            post_start = time.perf_counter()
            post = FbPost() 
            post.crawling_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            actions = ActionChains(self.driver)
            actions.move_to_element(self.post_el).perform()
            try:
                publish_time_str = self.extract_post_time(self.post_el)
                #如果未能获取当前post的time，用前一个post的time代替。
                if not publish_time_str:
                    publish_time_str = account.latest_time_str
                else:
                    account.latest_time_str = publish_time_str
                post.publish_time = datetime_util.parse_time(publish_time_str)
                DATE_CHECK, post.today_flag = datetime_util.check_date(post.publish_time, account)
            except Exception as e:
                post.publish_time = ''
                logger.exception(e)
            try:
                post.content = self.extract_post_content(self.post_el)
            except Exception as e:
                post.content = ''
                logger.exception(e)
            try:
                post.news_description = self.extract_post_news_description(self.post_el)
            except Exception as e:
                post.news_description = ''
                logger.exception(e)
            try:    
                post.up_num = util.parse_number(util.get_up_str(self.extract_post_up_number(self.post_el)))
            except Exception as e:
                post.up_num = 0
                logger.exception(e)
            try:                
                comment_num, retweet_num= self.extract_post_comment_retweet_number(self.post_el)
                post.comment_num = util.parse_number(util.get_retweet_comment_str(comment_num))
                post.retweet_num = util.parse_number(util.get_retweet_comment_str(retweet_num))
            except Exception as e:
                post.comment_num = 0
                post.retweet_num = 0
                logger.exception(e)
            if post.content:
                post.uuid = str(util.gen_uuid(post.content))
            else:
                post.uuid = str(util.gen_uuid(util.get_rand_char(8)))
            post.account = account.name
            if post.today_flag==0 and post.comment_num>comment_threshold:
                post.comment_flag = 1
                comment_list.extend(self.extract_post_comment(self.post_el, post.uuid, comment_max_count))  
            post_list.append(post)
            post_end = time.perf_counter()
            logger.debug(f'******runing time of extracting a post: {post_end-post_start}')
            self.post_el = self.get_post_el_by_waiting_check(self.post_el, self.post_sibling_el_xpath, scroll_detect_wait_time)
            WAIT_CHECK = False if self.post_failed else True    # check if the post is available or the net is too unstable to proceed.
            if len(post_list) > 5 or not DATE_CHECK or not WAIT_CHECK:
                return post_list, comment_list, DATE_CHECK, WAIT_CHECK

        
            
            




    
