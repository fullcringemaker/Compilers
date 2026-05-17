import re

class CalcToken:
    def __init__(self, token_type, value, line, column):
        self.type = token_type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return "CalcToken({0}, {1}, {2}, {3})".format(
            repr(self.type), repr(self.value), self.line, self.column
        )

class CalcLexerError(Exception):
    pass

TOKEN_SPECS = [
    ("WHITESPACE", r"[ \t\r\n]+"),
    ("n", r"[0-9]+"),
    ("plus sign", r"\+"),
    ("star", r"\*"),
    ("left paren", r"\("),
    ("right paren", r"\)"),
]

MASTER_REGEX = re.compile(
    "|".join("(?P<T{0}>{1})".format(index, pattern) for index, (_, pattern) in enumerate(TOKEN_SPECS))
)

INDEX_TO_TYPE = {"T{0}".format(index): name for index, (name, _) in enumerate(TOKEN_SPECS)}

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
            raise CalcLexerError(
                "Lexer error at line {0}, column {1}: unexpected character {2}".format(
                    line, column, repr(text[position])
                )
            )
        group_name = match.lastgroup
        token_type = INDEX_TO_TYPE[group_name]
        token_value = match.group(group_name)
        start_line = line
        start_column = column
        line, column = advance_position(token_value, line, column)
        position = match.end()
        if token_type == "WHITESPACE":
            continue
        if token_type == "n":
            value = int(token_value)
        else:
            value = token_value
        tokens.append(CalcToken(token_type, value, start_line, start_column))
    tokens.append(CalcToken("EOF", "", line, column))
    return tokens
