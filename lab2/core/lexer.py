import re
from core.exceptions import ParserError

VARIABLE_PATTERN = r"[a-zA-Z]"
TOKEN_PATTERN = rf"\s*({VARIABLE_PATTERN}|->|~|[!&|()])"
TOKEN_REGEX = re.compile(TOKEN_PATTERN)

def normalize(expression: str) -> str:
    return (expression
            .replace("→", "->")
            .replace("∨", "|")
            .replace("∧", "&")
            .replace("¬", "!"))

def tokenize(expression: str) -> list[str]:
    expression = normalize(expression)
    tokens = TOKEN_REGEX.findall(expression)
    joined = "".join(tokens).replace("->", "")
    original = expression.replace(" ", "").replace("->", "")
    if joined != original:
        raise ParserError("Обнаружены недопустимые символы")
    if not tokens:
        raise ParserError("Пустое выражение")
    return tokens