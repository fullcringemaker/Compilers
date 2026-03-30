import re

class Token:
    def __init__(self, tag, line, col, value):
        self.tag = tag
        self.line = line
        self.col = col
        self.value = value

    def __str__(self):
        return f"{self.tag} ({self.line}, {self.col}): {self.value}"

class Lexer:
    def __init__(self, text):
        self.text = text
        self.n = len(text)
        self.pos = 0
        self.line = 1
        self.col = 1

        self.re_ws = re.compile(r"[ \t\r\n]+")
        self.re_ident = re.compile(r"[A-Za-z][A-Za-z0-9]*")

        str_quoted = r"'(?:''|[^'\n])*'"
        str_code = r"\#[0-9]+"
        self.re_string = re.compile(rf"(?:{str_quoted}|{str_code})+")

        # Восьмеричные константы, как в Си: начинаются на 0 и состоят из восьмеричных цифр
        self.re_oct = re.compile(r"0[0-7]*")

        self.domains = [
            ("STRING", self.re_string),
            ("IDENT", self.re_ident),
            ("OCT", self.re_oct)
        ]

    def _advance_by_text(self, s):
        for ch in s:
            if ch == "\n":
                self.line += 1
                self.col = 1
            else:
                self.col += 1
        self.pos += len(s)

    def _peek_matches(self):
        if self.pos >= self.n:
            return False

        if self.re_ws.match(self.text, self.pos):
            return True

        for _, pat in self.domains:
            if pat.match(self.text, self.pos):
                return True

        return False

    def next_token(self):
        while True:
            if self.pos >= self.n:
                return None

            m_ws = self.re_ws.match(self.text, self.pos)
            if m_ws:
                self._advance_by_text(m_ws.group(0))
                continue

            best_tag = None
            best_lexeme = None
            best_len = 0

            for tag, pat in self.domains:
                m = pat.match(self.text, self.pos)
                if not m:
                    continue
                lexeme = m.group(0)
                L = len(lexeme)
                if L > best_len:
                    best_len = L
                    best_tag = tag
                    best_lexeme = lexeme

            if best_tag is not None:
                start_line = self.line
                start_col = self.col
                self._advance_by_text(best_lexeme)
                return Token(best_tag, start_line, start_col, best_lexeme)

            err_line = self.line
            err_col = self.col
            print(f"syntax error ({err_line},{err_col})")

            while self.pos < self.n and not self._peek_matches():
                self._advance_by_text(self.text[self.pos])

def main():
    with open(r"D:\лабы 3 курс\Compilers\lab1.2\input.txt", "r", encoding="utf-8") as f:
        text = f.read()
    lexer = Lexer(text)
    while True:
        tok = lexer.next_token()
        if tok is None:
            break
        print(tok)

if __name__ == "__main__":
    main()