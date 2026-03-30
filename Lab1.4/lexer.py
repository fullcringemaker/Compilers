TAG_WS = "WS"
TAG_IDENT = "IDENT"
TAG_INT = "INT"
TAG_KEYWORD = "KEYWORD"
TAG_OP = "OP"
TAG_COMMENT = "COMMENT"
TAG_EOF = "EOF"

CLASS_WS = 0
CLASS_DIGIT = 1
CLASS_K = 2
CLASS_E = 3
CLASS_Y = 4
CLASS_V = 5
CLASS_A = 6
CLASS_L = 7
CLASS_TILDE = 8
CLASS_OTHER_LETTER = 9
CLASS_OTHER = 10

CLASS_NAMES = [
    "WS",
    "DIGIT",
    "K",
    "E",
    "Y",
    "V",
    "A",
    "L",
    "TILDE",
    "OTHER_LETTER",
    "OTHER",
]

def build_generalized_symbols():
    arr = [CLASS_OTHER] * 128

    for ch in " \t\n\r":
        arr[ord(ch)] = CLASS_WS

    for ch in "0123456789":
        arr[ord(ch)] = CLASS_DIGIT

    arr[ord("k")] = CLASS_K
    arr[ord("e")] = CLASS_E
    arr[ord("y")] = CLASS_Y
    arr[ord("v")] = CLASS_V
    arr[ord("a")] = CLASS_A
    arr[ord("l")] = CLASS_L
    arr[ord("~")] = CLASS_TILDE

    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    for ch in letters:
        if ch not in "keyval":
            arr[ord(ch)] = CLASS_OTHER_LETTER

    return arr

GENERALIZED_SYMBOLS = build_generalized_symbols()

TRANSITIONS = [
    [1, 2, 4, 3, 3, 7, 3, 3, 10, 3, -1],
    [1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, 2, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [-1, 3, 3, 3, 3, 3, 3, 3, -1, 3, -1],
    [-1, 3, 3, 5, 3, 3, 3, 3, -1, 3, -1],
    [-1, 3, 3, 3, 6, 3, 3, 3, -1, 3, -1],
    [-1, 3, 3, 3, 3, 3, 3, 3, -1, 3, -1],  
    [-1, 3, 3, 3, 3, 3, 8, 3, -1, 3, -1],
    [-1, 3, 3, 3, 3, 3, 3, 9, -1, 3, -1],
    [-1, 3, 3, 3, 3, 3, 3, 3, -1, 3, -1],
    [12, 12, 12, 12, 12, 12, 12, 12, 11, 12, 12],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
    [12, 12, 12, 12, 12, 12, 12, 12, 13, 12, 12],
    [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1],
]

FINALS = [
    None,
    TAG_WS,
    TAG_INT,
    TAG_IDENT,
    TAG_IDENT,
    TAG_IDENT,
    TAG_KEYWORD,
    TAG_IDENT,
    TAG_IDENT,
    TAG_KEYWORD,
    None,
    TAG_OP,
    None,
    TAG_COMMENT,
]

IGNORED_TAGS = [TAG_WS]

class Position:
    def __init__(self, index, line, column):
        self.index = index
        self.line = line
        self.column = column

    def copy(self):
        return Position(self.index, self.line, self.column)

    def advance(self, ch):
        self.index += 1
        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

class Fragment:
    def __init__(self, start, follow):
        self.start = start
        self.follow = follow

    def __str__(self):
        return "(({}, {}), ({}, {}))".format(
            self.start.line,
            self.start.column,
            self.follow.line,
            self.follow.column
        )

class Token:
    def __init__(self, tag, fragment, lexeme):
        self.tag = tag
        self.fragment = fragment
        self.lexeme = lexeme

    def __str__(self):
        return "{} {}: {}".format(
            self.tag,
            self.fragment,
            escape_lexeme(self.lexeme)
        )

def escape_lexeme(s):
    result = []
    for ch in s:
        if ch == "\n":
            result.append("\\n")
        elif ch == "\t":
            result.append("\\t")
        elif ch == "\r":
            result.append("\\r")
        elif ch == "\\":
            result.append("\\\\")
        else:
            result.append(ch)
    return "".join(result)

class Lexer:
    def __init__(self, text):
        self.text = text
        self.position = Position(0, 1, 1)

    def class_of(self, ch):
        code = ord(ch)
        if 0 <= code < 128:
            return GENERALIZED_SYMBOLS[code]
        return -1

    def nextToken(self):
        while True:
            if self.position.index >= len(self.text):
                p = self.position.copy() 
                return Token(TAG_EOF, Fragment(p, p.copy()), "")

            token = self.read_one_token()

            if token is None:
                continue

            if token.tag in IGNORED_TAGS:
                continue

            return token

    def read_one_token(self):
        start = self.position.copy()
        probe = self.position.copy()
        state = 0

        last_final_state = -1
        last_final_position = None

        while probe.index < len(self.text):
            ch = self.text[probe.index]
            cls = self.class_of(ch)

            if cls == -1:
                next_state = -1
            else:
                next_state = TRANSITIONS[state][cls]

            if next_state == -1:
                break

            state = next_state
            probe.advance(ch)

            if FINALS[state] is not None:
                last_final_state = state
                last_final_position = probe.copy()

        if last_final_state != -1:
            lexeme = self.text[start.index:last_final_position.index]
            token = Token(
                FINALS[last_final_state],
                Fragment(start.copy(), last_final_position.copy()),
                lexeme
            )
            self.position = last_final_position.copy()
            return token

        if state == 10 or state == 12:
            if probe.index >= len(self.text):
                print(
                    "Лексическая ошибка в {}:{}: незавершённый комментарий".format(
                        start.line,
                        start.column
                    )
                )
                self.position = probe.copy()
                return None

        bad = self.text[self.position.index]
        print(
            "Лексическая ошибка в {}:{}: неожиданный символ {}".format(
                start.line,
                start.column,
                repr(bad)
            )
        )
        self.position.advance(bad)
        return None

def main():
    try:
        with open(r"D:\лабы 3 курс\Compilers\lab1.4\input.txt", "r", encoding="ascii") as f:
            text = f.read()
    except FileNotFoundError:
        print("Файл не найден")
        return
    except UnicodeDecodeError:
        print("Ошибка: входной файл должен быть ASCII")
        return

    lexer = Lexer(text)

    while True:
        token = lexer.nextToken()
        if token.tag == TAG_EOF:
            break
        print(token)

if __name__ == "__main__":
    main()