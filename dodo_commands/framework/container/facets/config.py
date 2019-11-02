class Config:
    def __init__(self):
        self.config = None

    @staticmethod
    def get(ctr):
        return ctr.config
