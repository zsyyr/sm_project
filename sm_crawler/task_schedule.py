import crawling_mode_parser
import crawler_exception as ce
import util
import crawler
import config_parser
import sys, os, stat
import functools, schedule, time, random, logging, yaml

# logger = logging.getLogger('crawler.task_schedule')

def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                print(traceback.format_exc())
                if cancel_on_failure:
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator

@catch_exceptions(cancel_on_failure=True)
def crawler_task(config, logger):
    sleep_time = random.randint(30, 600)
    logger.info(f'Task will start {sleep_time} seconds ago.')
    time.sleep(sleep_time)
    crawler.main(config)


def init_log_config(path_prefix):
    try:
        # if not os.path.exists(path_prefix + 'log/'):
        #     os.makedirs(path_prefix + 'log/')
        logging_path = path_prefix + 'logconf.yml'
        print(logging_path)
        dict_conf = {}
        with open(logging_path, "r", encoding='utf-8') as f:
            dict_conf = yaml.safe_load(f)
        dict_conf['handlers']['fh']['filename'] = path_prefix + dict_conf['handlers']['fh']['filename']
        logging.config.dictConfig(dict_conf)
        # os.chmod(path_prefix + 'log/', stat.S_IWOTH)
        logger = logging.getLogger('crawler.task_schedule')
        return logger
    except ce.LogConfigException as e:
        print(e)
        
def run_daily_crawling_task(config, logger):
    daily_start_time = config.daily_start_hour
    logger.info(f'Task will start everday at {daily_start_time}.')
    schedule.every().day.at(daily_start_time).do(crawler_task, config, logger)
    while True:
        schedule.run_pending()
        time.sleep(1)
        
def run_single_crawling_task(config, logger):
    crawler.main(config)
    
def fit_crawling_task(config, logger):
    if config.task_mode == 'single_task':
        run_single_crawling_task(config, logger)
    elif config.task_mode == 'daily_task':
        run_daily_crawling_task(config, logger)

def run_crawling_task():
    try:
        crawling_mode, task_mode, auth_mode  =crawling_mode_parser.crawling_mode_parse()  
        path_prefix = util.parse_prefix_path(crawling_mode)
        try:
            logger = init_log_config(path_prefix)
            logger.info(f'crawling mode is: {crawling_mode}, task mode is: {task_mode}, auth mode is: {auth_mode}')
        except ce.LoginException as e:
            logger.exception(e)
            logger.critical('Log config failed, please check logconf.yml')
        try: 
            config = config_parser.CrawlingConfig(crawling_mode, task_mode, auth_mode, path_prefix)
        except ce.ConfigException:
            logger.critical('Config parse failed, please check crawler_conf.yml and restart.')
            raise ce.ExitException
        try:
            fit_crawling_task(config, logger)
        except Exception as e:
            logger.exception(e)
            raise ce.ExitException    
    except ce.ExitException as e:
        print(e)
    except SystemExit as e:
        logger.critical('Crawling task stopped anomally!')
        # sys.exit()
        
run_crawling_task()
