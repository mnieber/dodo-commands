class Config:
    def __init__(self):
        self.config = None
        self.warnings = []

    @staticmethod
    def get(ctr):
        return ctr.config
