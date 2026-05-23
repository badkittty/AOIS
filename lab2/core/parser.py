from core.ast_nodes import Variable, Not, And, Or, Implication, Equivalence
from core.exceptions import ParserError
from core.lexer import tokenize

PRIORITY = {
    "!": 5,
    "&": 4,
    "|": 3,
    "->": 2,
    "~": 1,
}
BINARY_OPERATORS = {"&", "|", "->", "~"}

class Parser:
    def __init__(self, expression: str) -> None:
        self.tokens = tokenize(expression)

    def parse(self):
        rpn = self._to_rpn()
        return self._build_ast(rpn)

    def _to_rpn(self) -> list[str]:
        output = []
        stack = []
        for token in self.tokens:
            if token.isalpha():
                output.append(token)
            elif token == "!":
                stack.append(token)
            elif token in PRIORITY:
                while (stack and stack[-1] != "(" and
                       PRIORITY.get(stack[-1], 0) >= PRIORITY[token]):
                    output.append(stack.pop())
                stack.append(token)
            elif token == "(":
                stack.append(token)
            elif token == ")":
                self._process_closing_bracket(stack, output)
        while stack:
            output.append(stack.pop())
        return output

    def _process_closing_bracket(self, stack: list, output: list) -> None:
        while stack and stack[-1] != "(":
            output.append(stack.pop())
        if stack and stack[-1] == "(":
            stack.pop()
        else:
            raise ParserError("Несогласованные скобки")

    def _build_ast(self, rpn: list[str]):
        stack = []
        for token in rpn:
            if token.isalpha():
                stack.append(Variable(token))
            elif token == "!":
                operand = stack.pop()
                stack.append(Not(operand))
            elif token == "&":
                right, left = stack.pop(), stack.pop()
                stack.append(And(left, right))
            elif token == "|":
                right, left = stack.pop(), stack.pop()
                stack.append(Or(left, right))
            elif token == "->":
                right, left = stack.pop(), stack.pop()
                stack.append(Implication(left, right))
            elif token == "~":
                right, left = stack.pop(), stack.pop()
                stack.append(Equivalence(left, right))
            else:
                raise ParserError(f"Неизвестный оператор: {token}")
        if len(stack) != 1:
            raise ParserError("Некорректное выражение")
        return stack[0]

def parse(expression: str):
    return Parser(expression).parse()