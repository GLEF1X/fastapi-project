from typing import Protocol


class PasswordHasherProto(Protocol):

    def hash(self, password: str) -> str: ...

    def check_needs_rehash(self, hash: str) -> bool: ...

    def verify(self, hash: str, password: str) -> bool: ...