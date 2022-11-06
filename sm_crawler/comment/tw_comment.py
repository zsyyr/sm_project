from .comment import Comment

class TwComment(Comment):
    def __init__(self):
        super().__init__()
        self.platform = 'TW'
        self.type = 'comment'