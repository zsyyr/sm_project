from abc import ABC, abstractmethod


class Writer(ABC):
    def __init__(self):
        """根据需要，初始化结果路径、初始化表头、初始化数据库等"""
        pass

    @abstractmethod
    def write_posts(self, posts):
        """给定信息，写入对应文本或数据库"""
        pass

    @abstractmethod
    def write_comments(self, comments):
        """给定信息，写入对应文本或数据库"""
        pass

    @abstractmethod
    def write_account(self, user):
        """给定用户信息，写入对应文本或数据库"""
        pass