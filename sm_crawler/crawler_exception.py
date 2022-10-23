from ctypes.wintypes import SMALL_RECT


class SmCrawlerException(Exception):
    pass

class LogConfigException(SmCrawlerException):
    pass

class LoginException(SmCrawlerException):
    pass

class ConfigException(SmCrawlerException):
    pass

class StoreException(SmCrawlerException):
    pass

class ExitException(SmCrawlerException):
    pass