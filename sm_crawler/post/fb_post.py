from .post import Post

class FbPost(Post):
    def __init__(self):
        super().__init__()
        self.platform = 'FB'
        self.type = 'post'
        self.comment_flag = 0
