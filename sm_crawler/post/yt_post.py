from .post import Post

class YtPost(Post):
    def __init__(self):
        super().__init__()
        self.platform = 'YT'
        self.type = 'post'
        self.comment_flag = 0
        self.views_num = 0
