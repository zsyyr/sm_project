from .post import Post

class TwPost(Post):
    def __init__(self):
        super().__init__()
        self.platform = 'TW'
        self.type = 'post'
        self.comment_flag = 0
