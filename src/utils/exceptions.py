class UserIsUnauthorized(Exception):
    def __init__(self, hint: str):
        self.hint = hint
