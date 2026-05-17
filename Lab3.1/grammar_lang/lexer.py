import re

class Token:
    def __init__(self, token_type, value, line, column):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return "Token({0}, {1}, {2}, {3})".format(
            repr(self.type), repr(self.value), self.line, self.column
        )

class LexerError(Exception):
    pass

TOKEN_SPECS = [
    ("COMMENT", r"\(\*[\s\S]*?\*\)"),
    ("WHITESPACE", r"[ \t\r\n]+"),
    ("KW_TOKENS", r"tokens\b"),
    ("KW_IS", r"is\b"),
    ("KW_START", r"start\b"),
    ("LPAREN", r"\("),
    ("RPAREN", r"\)"),
    ("COMMA", r","),
    ("DOT", r"\."),
    ("IDENT", r"[A-Za-z_]+"),
    ("NUMBER", r"[0-9]+"),
]

MASTER_REGEX = re.compile(
    "|".join("(?P<{0}>{1})".format(name, pattern) for name, pattern in TOKEN_SPECS)
)

SKIP_TYPES = {"COMMENT", "WHITESPACE"}

def advance_position(text, line, column):
    for ch in text:
        if ch == "\n":
            line += 1
            column = 1
        else:
            column += 1
    return line, column

def tokenize(text):
    tokens = []
    position = 0
    line = 1
    column = 1

    while position < len(text):
        match = MASTER_REGEX.match(text, position)
        if match is None:
            bad_char = text[position]
            raise LexerError(
                "Lexer error at line {0}, column {1}: unexpected character {2}".format(
                    line, column, repr(bad_char)
                )
            )

        token_type = match.lastgroup
        token_value = match.group(token_type)
        start_line = line
        start_column = column

        line, column = advance_position(token_value, line, column)
        position = match.end()

        if token_type in SKIP_TYPES:
            continue

        tokens.append(Token(token_type, token_value, start_line, start_column))

    tokens.append(Token("EOF", "", line, column))
    return tokens
