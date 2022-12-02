class Account():
    def __init__(self, name, platform, url, stop_date, crawling_comment_flag=1):
        self.name = name
        self.type = 'account'
        self.nickname = ''
        self.id = 0
        self.platform = platform
        self.url = url
        self.crawling_comment_flag = crawling_comment_flag
        self.gender = ''
        self.location = ''
        self.birthday = ''
        self.description = ''
        self.verified_reason = ''
        self.talent = ''
        self.education = ''
        self.work = ''
        self.following = 0
        self.followers = 0
        self.start_time = ''
        self.begin_date = ''
        self.end_date = ''
        self.stop_date = stop_date
        self.crawling_post_number = 0
        self.latest_time_str = ''
        self.temp_height = 0
        

    def __str__(self):
        """print a poster"""
        result = self.name + '\n'
        result += u'nickname:%d\n' % self.nickname
        result += u'platform:%s\n' % self.platform
        result += u'url:%s\n' % self.url
        result += u'gender:%s\n' % self.gender
        result += u'description:%s\n' % self.description
        result += u'platform:%s\n' % self.platform
        result += u'following:%d\n' % self.following
        result += u'followers:%d\n' % self.followers
        result += u'start time:s\n' % self.start_time
        return result