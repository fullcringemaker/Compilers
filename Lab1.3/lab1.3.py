from enum import Enum

class DomainTag(Enum):
    IDENT = "IDENT"
    INT = "INT"
    STRING = "STRING"
    EOF = "EOF"

class Position:
    def __init__(self, text, index=0, line=1, column=1):
        self.text = text
        self.index = index
        self.line = line
        self.column = column

    def copy(self):
        return Position(self.text, self.index, self.line, self.column)

    def current_char(self):
        if self.index >= len(self.text):
            return None
        return self.text[self.index]

    def is_eof(self):
        return self.index >= len(self.text)

    def advance(self):
        if self.is_eof():
            return

        ch = self.text[self.index]
        self.index += 1

        if ch == "\r":
            if self.index < len(self.text) and self.text[self.index] == "\n":
                self.index += 1
            self.line += 1
            self.column = 1
        elif ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

class Fragment:
    def __init__(self, start, follow):
        self.start = start.copy()
        self.follow = follow.copy()

    def __str__(self):
        return f"({self.start.line}, {self.start.column})-({self.follow.line}, {self.follow.column})"

class Message:
    def __init__(self, is_error, text, position):
        self.is_error = is_error
        self.text = text
        self.position = position.copy()

    def __str__(self):
        kind = "ERROR" if self.is_error else "WARNING"
        return f"{kind} ({self.position.line}, {self.position.column}): {self.text}"

class Compiler:
    def __init__(self):
        self.messages = []
        self.name_codes = {}
        self.names = []

    def add_error(self, position, text):
        self.messages.append(Message(True, text, position))

    def add_name(self, name):
        if name not in self.name_codes:
            code = len(self.names)
            self.name_codes[name] = code
            self.names.append(name)
        return self.name_codes[name]

class Token:
    def __init__(self, tag, coords):
        self.tag = tag
        self.coords = coords

    def has_attr(self):
        return False

    def attr_to_string(self):
        return ""

    def __str__(self):
        if self.has_attr():
            return f"{self.tag.value} {self.coords}: {self.attr_to_string()}"
        return f"{self.tag.value} {self.coords}:"

class IdentToken(Token):
    def __init__(self, coords, code):
        super().__init__(DomainTag.IDENT, coords)
        self.code = code

    def has_attr(self):
        return True

    def attr_to_string(self):
        return str(self.code)

class IntToken(Token):
    def __init__(self, coords, value):
        super().__init__(DomainTag.INT, coords)
        self.value = value

    def has_attr(self):
        return True

    def attr_to_string(self):
        return str(self.value)

class StringToken(Token):
    def __init__(self, coords, value):
        super().__init__(DomainTag.STRING, coords)
        self.value = value

    def has_attr(self):
        return True

    def attr_to_string(self):
        return self.value

class EOFToken(Token):
    def __init__(self, coords):
        super().__init__(DomainTag.EOF, coords)

class Scanner:
    def __init__(self, program, compiler):
        self.program = program
        self.compiler = compiler
        self.cur = Position(program)

    def is_space(self, ch):
        return ch in " \t\n\r"

    def is_digit(self, ch):
        return "0" <= ch <= "9"

    def is_letter(self, ch):
        return ("a" <= ch <= "z") or ("A" <= ch <= "Z")

    def is_ident_start(self, ch):
        return self.is_letter(ch) or ch in "_$@"

    def is_ident_part(self, ch):
        return self.is_letter(ch) or self.is_digit(ch) or ch in "_$@"

    def skip_spaces(self):
        while not self.cur.is_eof() and self.is_space(self.cur.current_char()):
            self.cur.advance()

    def next_token(self):
        while True:
            self.skip_spaces()
            start = self.cur.copy()

            if self.cur.is_eof():
                return EOFToken(Fragment(start, self.cur))

            ch = self.cur.current_char()

            if self.is_ident_start(ch):
                return self.read_ident()

            if self.is_digit(ch):
                return self.read_number()

            if ch == '"':
                token = self.read_string()
                if token is not None:
                    return token
                continue

            self.compiler.add_error(self.cur, f"Unexpected symbol: {ch}")
            self.cur.advance()

    def read_ident(self):
        start = self.cur.copy()
        lexeme = ""

        while not self.cur.is_eof():
            ch = self.cur.current_char()
            if not self.is_ident_part(ch):
                break
            lexeme += ch
            self.cur.advance()

        code = self.compiler.add_name(lexeme)
        return IdentToken(Fragment(start, self.cur), code)

    def read_number(self):
        start = self.cur.copy()
        raw = ""

        while not self.cur.is_eof():
            ch = self.cur.current_char()
            if self.is_digit(ch) or ch == "_":
                raw += ch
                self.cur.advance()
            else:
                break

        digits_only = raw.replace("_", "")

        if digits_only == "":
            self.compiler.add_error(start, "Invalid integer literal")
            return None
        value = int(digits_only)
        return IntToken(Fragment(start, self.cur), value)

    def read_string(self):
        start = self.cur.copy()
        self.cur.advance()

        value = ""

        while not self.cur.is_eof():
            ch = self.cur.current_char()

            if ch == '"':
                self.cur.advance()
                return StringToken(Fragment(start, self.cur), value)

            if ch == "\n" or ch == "\r":
                self.compiler.add_error(self.cur, "String literal cannot cross line boundary")
                return None

            if ch == "\\":
                escape_pos = self.cur.copy()
                self.cur.advance()

                if self.cur.is_eof():
                    self.compiler.add_error(escape_pos, "Unterminated string literal")
                    return None

                esc = self.cur.current_char()

                if esc == "n":
                    value += "\n"
                    self.cur.advance()
                    continue
                elif esc == '"':
                    value += '"'
                    self.cur.advance()
                    continue
                elif esc == "t":
                    value += "\t"
                    self.cur.advance()
                    continue
                elif esc == "\\":
                    value += "\\"
                    self.cur.advance()
                    continue
                else:
                    self.compiler.add_error(escape_pos, f"Unknown escape sequence: \\{esc}")

                    while not self.cur.is_eof():
                        if self.cur.current_char() == '"':
                            self.cur.advance()
                            break
                        if self.cur.current_char() == "\n" or self.cur.current_char() == "\r":
                            break
                        self.cur.advance()
                    return None

            value += ch
            self.cur.advance()

        self.compiler.add_error(start, "Unterminated string literal")
        return None

def main():
    compiler = Compiler()

    with open(r"D:\лабы 3 курс\Compilers\lab1.3\input.txt", "r", encoding="utf-8") as f:
        program = f.read()

    scanner = Scanner(program, compiler)

    print("TOKENS:")
    while True:
        token = scanner.next_token()
        print(token)
        if token.tag == DomainTag.EOF:
            break

    print()
    print("Identifier table:")
    if len(compiler.names) == 0:
        print("Empty")
    else:
        for i in range(len(compiler.names)):
            print(f"{i}: {compiler.names[i]}")

    print()
    print("Messages:")
    if len(compiler.messages) == 0:
        print("No messages")
    else:
        for message in compiler.messages:
            print(message)

if __name__ == "__main__":
    main()
