from typing import Any, Optional

class Record:
    def __init__(self):
        self.id: Optional[str] = None
        self.c: int = 0
        self.u: int = 0
        self.t: int = 0
        self.l: int = 0
        self.d: int = 0
        self.po: Optional[int] = None
        self.pi: Any = None

    def is_free(self) -> bool:
        return self.u == 0

    def is_deleted(self) -> bool:
        return self.d == 1

    def __repr__(self):
        return f"Record(id={self.id}, c={self.c}, u={self.u}, t={self.t}, l={self.l}, d={self.d}, po={self.po}, pi={self.pi})"