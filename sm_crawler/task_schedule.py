import crawler
import config_parser
import functools, schedule, time, random

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
    time.sleep(sleep_time)
    crawler.main()
    
config = config_parser.get_yaml_config()
everyday_start_time = config['everyday_start_hour']
schedule.every().day.at(everyday_start_time).do(crawler_task)
while True:
    schedule.run_pending()
    time.sleep(1)