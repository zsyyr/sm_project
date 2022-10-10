from .comment import Comment

class FbComment(Comment):
    def __init__(self):
        super().__init__()
        self.platform = 'FB'
        self.type = 'comment'