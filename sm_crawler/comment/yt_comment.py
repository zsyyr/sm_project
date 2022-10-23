from .comment import Comment

class YtComment(Comment):
    def __init__(self):
        super().__init__()
        self.platform = 'YT'
        self.type = 'comment'