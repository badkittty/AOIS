from __future__ import annotations
from abc import ABC, abstractmethod

class Node(ABC):
    @abstractmethod
    def evaluate(self, context: dict[str, int]) -> int:
        pass

    @abstractmethod
    def get_vars(self) -> set[str]:
        pass

class Variable(Node):
    def __init__(self, name: str) -> None:
        self.name = name

    def evaluate(self, context: dict[str, int]) -> int:
        return context[self.name]

    def get_vars(self) -> set[str]:
        return {self.name}

class UnaryNode(Node, ABC):
    def __init__(self, operand: Node) -> None:
        self.operand = operand

    def get_vars(self) -> set[str]:
        return self.operand.get_vars()

class BinaryNode(Node, ABC):
    def __init__(self, left: Node, right: Node) -> None:
        self.left = left
        self.right = right

    def get_vars(self) -> set[str]:
        return self.left.get_vars() | self.right.get_vars()

class Not(UnaryNode):
    def evaluate(self, context: dict[str, int]) -> int:
        return 1 - self.operand.evaluate(context)

class And(BinaryNode):
    def evaluate(self, context: dict[str, int]) -> int:
        return self.left.evaluate(context) & self.right.evaluate(context)

class Or(BinaryNode):
    def evaluate(self, context: dict[str, int]) -> int:
        return self.left.evaluate(context) | self.right.evaluate(context)

class Implication(BinaryNode):
    def evaluate(self, context: dict[str, int]) -> int:
        return (1 - self.left.evaluate(context)) | self.right.evaluate(context)

class Equivalence(BinaryNode):
    def evaluate(self, context: dict[str, int]) -> int:
        return int(self.left.evaluate(context) == self.right.evaluate(context))