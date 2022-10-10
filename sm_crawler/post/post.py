class Post:
    def __init__(self):
        self.account = ''
        self.publish_time = ''
        self.uuid = ''
        self.content = ''
        self.video_src = ''
        self.news_description = ''
        self.up_num = 0
        self.retweet_num = 0    
        self.comment_num = 0       
        self.platform = ''
        self.publish_place = ''
        self.crawling_time = ''
        self.trend = []
        self.today_flag = 0

    def __str__(self):
        """print a post"""
        result = u'content:%s\n' % self.content
        result += u'uuid:%s\n' % self.uuid
        result += u'account:%s\n' % self.account
        result += u'publish time:%s\n' % self.publish_time
        result += u'platform:%s\n' % self.platform
        result += u'up number:%d\n' % self.up_num
        result += u'retweet number:%d\n' % self.retweet_num
        result += u'comment number:%d\n' % self.comment_num
        result += u'today:%d\n' % self.today_flag
        return result