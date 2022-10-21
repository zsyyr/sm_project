import crawler
import config_parser
import functools, schedule, time, random, logging

logger = logging.getLogger('task_schedule')

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
def crawler_task():
    sleep_time = random.randint(30, 600)
    logger.info(f'Task will start {sleep_time} seconds ago.')
    time.sleep(sleep_time)
    crawler.main()
    
config = config_parser.get_yaml_config()
daily_start_time = config['daily_start_hour']
logger.info(f'Task will start everday at {daily_start_time}.')
schedule.every().day.at(daily_start_time).do(crawler_task)
while True:
    schedule.run_pending()
    time.sleep(1)