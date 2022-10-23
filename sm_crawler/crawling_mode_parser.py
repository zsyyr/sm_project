import sys
import getopt

def crawling_mode_parse():
    '''
    crawling_mode = ['browser_debug',               #直接运行程序连接debug模式下的browser，无docker，方便调试。默认模式。
                     'browser_debug_docker',        #启动docker运行程序连接debug模式下的browser，需要与browser相适配的webdriver tool。                     
                     'selenium_grid_docker']        #共启动4个docker：sm_crawler docker、mongo docker、selenium-hub(selenium grid) docker、chrome(selenium node) docker
                     
    authorization_mode = ['browser_auto',           #采用默认login模式登陆网站平台（账户、密码存储于browser自动登陆）。默认模式。    
                  'email_pwd',                      #采用用户email、pwd登陆网站平台，平台用户email、pwd配置于crawler_conf.yml。
                  'cookies']                        #采用cookies登陆，cookies 文件路径配置于crawler_conf.yml。
                  
    task_mode = ['single_task',                     #单次任务模式，通过crawler_conf.yml中的single_task_config获取任务信息。默认模式。    
                 'daily_task']                      #每日任务模式，每日定时采集，通过crawler_conf.yml获取任务信息。
    
    eg: python task_schedule.py -m selenium_grid_docker -a browser_auto -t daily_task
    '''
    mode = None  
    auth = None
    task = None
    argv = sys.argv[1:]
    try:
        opts, args = getopt.getopt(argv, "m:a:t:") 
    except:
        print("Error")
    for opt, arg in opts:
        if opt in ['-m']:
            mode = arg
        elif opt in ['-a']:
            auth = arg
        elif opt in ['-t']:
            task = arg
    if not mode:
        mode = 'browser_debug'
    if not auth:
        auth = 'browser_auto'
    if not task:
        task = 'single_task'
    return mode, task, auth

if __name__ == '__main__': 
    crawling_mode,  task_mode, auth_mode =crawling_mode_parse()    
    print(crawling_mode, task_mode, auth_mode)