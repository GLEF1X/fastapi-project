from typing import Optional


class UnableToDelete(Exception):
    def __init__(self, msg: Optional[str] = None):
        self.message = msg

    def __str__(self) -> str:
        return f"<Exception {self} message={self.message}>"
