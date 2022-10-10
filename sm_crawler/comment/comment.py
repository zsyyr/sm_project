class Comment():
    def __init__(self):        
        self.author = ''
        self.post_uuid = ''
        self.publish_time = ''
        self.uuid = 0
        self.content = ''
        self.up_num = 0
        self.retweet_num = 0    
        self.extract_time = ''
        self.platform = ''
        self.publish_place = ''

    def __str__(self):
        """print a comment"""
        result = u'author:%s\n' % self.author
        result += u'content:%s\n' % self.content
        result += u'publish time:%s\n' % self.publish_time
        result += u'extract time:%d\n' % self.extract_time
        result += u'platform:%s\n' % self.platform
        result += u'up number:%d\n' % self.up_num
        result += u'retweet number:%d\n' % self.retweet_num
        result += u'publish place:%s\n' % self.publish_place
        return result 