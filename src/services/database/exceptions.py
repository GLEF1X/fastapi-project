class DatabaseError(Exception):
    def __init__(self, orig: Exception):
        self.orig = orig

    def __str__(self) -> str:
        return f"<Exception {self} message={self.orig}>. Original exception traceback:" + self.orig.__str__()
