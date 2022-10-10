from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import logging
import json
import os
from .driver import Driver
from util import Singleton

logger = logging.getLogger('crawler.chrome_driver')

@Singleton
class ChromeWebDriver(Driver):
    def __init__(self):        
        self.driver = None
        self.service = None
        self.options = None
        self.web_driver_path = None
        self.extract_task = None
        self.current_window_handle = None
        
    def remote_options_config(self, remote_debugger_address):
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("debuggerAddress", remote_debugger_address)
    
    def options_config(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('window-size=1920x3000')
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--headless")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--disable-software-rasterizer")
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--ignore-certificate-errors')
        self.options.add_argument('--allow-running-insecure-content')
        self.options.add_argument('blink-settings=imagesEnabled=false')
        disk_cache_config = "--disk-cache-dir=" + "'" + os.getcwd() + os.sep + "data/chrome-cache/'"
        self.options.add_argument(disk_cache_config)
        self.options.add_experimental_option('excludeSwitches', ['enable-automation'])
        self.options.add_experimental_option('useAutomationExtension', False)
        # self.options.add_argument('--headless')
        # self.options.add_extension('./driver/plugin/FastStunnel_v1.607.crx')
          
    def service_config(self):
        self.service = Service(executable_path=self.web_driver_path) 
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                                    'source': 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'})   
        # self.driver.execute_cdp_cmd("Network.setBlockedURLs",{
        #                             "urls":["*.flv*","*.png","*.jpg*","*.jepg*","*.gif*"]})

    def get_selenium_grid_driver(self, selenium_grid_url):
        # selenium_grid_url = "http://127.0.0.1:4444/wd/hub"
        CHROME= {"browserName": "chrome"}
        return webdriver.Remote(desired_capabilities=CHROME,command_executor=selenium_grid_url)

    def vpn_config(self):
        self.driver.execute_script("window.open();")
        handles = self.driver.window_handles
        self.driver.switch_to.window(handles[-1])
        self.driver.get("extension://bblcccknbdbplgmdjnnikffefhdlobhp/login.html")        
        self.driver.find_element_by_link_text("Login").click()      
        # self.driver.find_element_by_xpath("//a[text()='Login']").send_keys(Keys.ENTER)
        self.driver.find_element_by_id("email_l").send_keys("zmszsyyr@163.com")
        self.driver.find_element_by_id("password_l").send_keys("vpn2020")
        self.driver.find_element_by_id("btn_l").click()        

    def save_cookies(self):
        # time.sleep(3)
        self._cookies_file = './data/cookies/cookies.txt'
        with open('./data/cookies/cookies.txt','w') as f:
        # 将cookies保存为json格式
            f.write(json.dumps(self.driver.get_cookies()))
    
    def load_cookies(self):
        self.driver.delete_all_cookies()
        with open('./data/cookies/cookies.txt','r') as f:
        # 使用json读取cookies 注意读取的是文件 所以用load而不是loads
            cookies_list = json.load(f)
            # 方法1 将expiry类型变为int
            # for cookie in cookies_list:
            #     # 并不是所有cookie都含有expiry 所以要用dict的get方法来获取
            #     if isinstance(cookie.get('expiry'), float):
            #         cookie['expiry'] = int(cookie['expiry'])
            #     self.driver.add_cookie(cookie)
            for cookie in cookies_list:
                # 该字段有问题所以删除就可以 
                if 'expiry' in cookie:
                    del cookie['expiry']
                self.driver.add_cookie(cookie)

    def delete_all_cookies(self):
        self.driver.delete_all_cookies()    #for clean cache
        
    # def get_cookies(self):
    #     if(os.path.exists(self._cookies_file) == False) :
    #         self.save_cookies()
    #     else :
    #         self.load_cookies()

    def open_tab_by_url(self, website_url, timeout=3):   
        logger.info(f'open url {website_url}')     
        self.driver.switch_to.new_window('tab')
        self.driver.implicitly_wait(timeout)
        self.driver.get(website_url)
        time.sleep(timeout)
        
        self.current_window_handle = self.driver.current_window_handle
        for window_handle in self.driver.window_handles:
            if window_handle != self.current_window_handle:
                self.driver.switch_to.window(window_handle)
                self.driver.close()
        self.driver.switch_to.window(self.current_window_handle)
        logger.info('Target url opende, previous url tags closed!')

    def open_tab_by_url_with_cookies(self, website_url, timeout=3):   
        logger.info(f'open url {website_url}')     
        self.driver.switch_to.new_window('tab')
        self.driver.implicitly_wait(timeout)        
        self.driver.get(website_url)        #must open the target website befor add_cookies
        self.load_cookies()
        time.sleep(2)
        self.driver.get(website_url)      #add cookies then reopen the website. driver.refresh() do not make sense!
        time.sleep(timeout)
        logger.info('url opende')

    def auto_scroll(self, distance=0):
        if distance:
            self.driver.execute_script(f"window.scrollBy(0,{distance})")
        else:
            self.driver.execute_script("window.scrollTo(0 ,document.body.scrollHeight)")
   
    def close_tag(self):
        logger.info('account page tag closed!')
        self.driver.close()

    def close_driver(self):
        self.driver.quit()  
    



# if __name__ == '__main__':