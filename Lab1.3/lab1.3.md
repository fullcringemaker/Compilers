% Лабораторная работа № 1.3 «Объектно-ориентированный
  лексический анализатор»
% 16 марта 2026 г.
% Дмитрий Трофименко, ИУ9-62Б

# Цель работы
Целью данной работы является приобретение навыка реализации лексического анализатора на 
объектно-ориентированном языке без применения каких-либо средств автоматизации решения задачи 
лексического анализа.

# Индивидуальный вариант
- Строковые литералы: ограничены двойными кавычками, не могут пересекать границы строк текста, содержат escape-последовательности «\n», «\"», «\t» и «\\».
- Целые числа: последовательности десятичных знаков и знаков «_», начинающиеся с цифры (прочерк не влияет на значение числа).
- Идентификаторы: состоят из латинских букв, цифр и знаков «_», «$», «@», не могут начинаться на цифру.

## Лексический домен для защиты
Добавить escape-последовательность \xHH, где HH - шестнадцатеричный код символа

# Реализация

## Файл `lexer.py`
```python
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

    # Добавить escape-последовательность \xHH, где HH - шестнадцатеричный код символа
                elif esc == "x":
                    self.cur.advance()
                    ch = self.cur.current_char()
                    if ("0" <= ch <= "9") or ("a" <= ch <= "f") or ("A" <= ch <= "F"):
                        hexcode = ch
                        self.cur.advance()
                        ch = self.cur.current_char()
                        if ("0" <= ch <= "9") or ("a" <= ch <= "f") or ("A" <= ch <= "F"):
                            hexcode += ch
                            value += chr(int(hexcode, 16))
                            self.cur.advance()
                        else: 
                            self.compiler.add_error(escape_pos, "wrong hex")
                    else:
                        self.compiler.add_error(escape_pos, "wrong hex")
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
```

# Тестирование

Входные данные

```text
abc
_name
$123user123
@temp
a1_b2$c3@d4
brep

123
1_234
33_7
5___6

"hello"  "code 30 is \x30" "code 4F is \x4f"
"line\nbreak"
"quote: \""
"tab\tend"
"slash \\"

abc123 "test" 45_67 @name

"unfinished
12a
#
bad&token
"wrong\qescape"
```

Вывод на `stdout`

```shell
TOKENS:
IDENT (1, 1)-(1, 4): 0
IDENT (2, 1)-(2, 6): 1
IDENT (3, 1)-(3, 12): 2
IDENT (4, 1)-(4, 6): 3
IDENT (5, 1)-(5, 12): 4
IDENT (6, 1)-(6, 5): 5
INT (8, 1)-(8, 4): 123
INT (9, 1)-(9, 6): 1234
INT (10, 1)-(10, 5): 337
INT (11, 1)-(11, 6): 56
STRING (13, 1)-(13, 8): hello
STRING (13, 10)-(13, 27): code 30 is 0
STRING (13, 28)-(13, 45): code 4F is O
STRING (14, 1)-(14, 14): line
break
STRING (15, 1)-(15, 12): quote: "
STRING (16, 1)-(16, 11): tab    end
STRING (17, 1)-(17, 11): slash \
IDENT (19, 1)-(19, 7): 6
STRING (19, 8)-(19, 14): test
INT (19, 15)-(19, 20): 4567
IDENT (19, 21)-(19, 26): 7
INT (22, 1)-(22, 3): 12
IDENT (22, 3)-(22, 4): 8
IDENT (24, 1)-(24, 4): 9
IDENT (24, 5)-(24, 10): 10
EOF (25, 16)-(25, 16):

Identifier table:
0: abc
1: _name
2: $123user123
3: @temp
4: a1_b2$c3@d4
5: brep
6: abc123
7: @name
8: a
9: bad
10: token

Messages:
ERROR (21, 12): String literal cannot cross line boundary
ERROR (23, 1): Unexpected symbol: #
ERROR (24, 4): Unexpected symbol: &
ERROR (25, 7): Unknown escape sequence: \q
```

# Вывод
В данной лабораторной работе были реализованы чтение входного текста из файла и лексический анализ, 
который по последовательности символов выделяет лексемы, определяет их тип и вычисляет координаты 
начала и конца каждого фрагмента. В соответствии с требованиями, для каждой распознанной единицы 
формируется описание для вывода в стандартный поток, а для лексем с атрибутами дополнительно 
вычисляется и выводится их значение, чтобы результат анализа был пригоден для дальнейшей передачи 
в синтаксический разбор.

В процессе выполнения работы были реализованы правила распознавания доменов индивидуального варианта 
и вычисление их атрибутов. Для идентификаторов формируется таблица имён и каждому встреченному имени 
сопоставляется номер, что позволяет не хранить повторяющиеся строки в потоке токенов. Для целых чисел 
обеспечено корректное получение числового значения независимо от наличия разделителей внутри записи. 
Для строковых литералов выполняется построение фактического содержимого строки с обработкой 
escape-последовательностей, включая расширение с шестнадцатеричным кодом символа, при этом 
контролируется запрет на переход через границу строки текста.

Отдельно была реализована обработка ошибок и восстановление после них, чтобы анализатор не прекращал 
работу при встрече некорректного фрагмента. При обнаружении недопустимого символа или неверной формы 
литерала формируется сообщение с координатой, после чего выполняется продвижение по входу до точки, 
где снова возможно распознавание следующей лексемы. Тестирование на примерах с корректными 
конструкциями и намеренно внесёнными ошибками показало, что лексемы выделяются стабильно, координаты 
рассчитываются правильно, таблица идентификаторов заполняется последовательно, а сообщения об ошибках 
помогают локализовать проблему и при этом не мешают продолжению анализа текста.
