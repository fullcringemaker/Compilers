% Лабораторная работа № 1.2. «Лексический анализатор
  на основе регулярных выражений»
% 4 марта 2026 г.
% Дмитрий Трофименко, ИУ9-62Б

# Цель работы
Целью данной работы является приобретение навыка разработки простейших лексических анализаторов, 
работающих на основе поиска в тексте по образцу, заданному регулярным выражением.

# Индивидуальный вариант
Идентификаторы: последовательности латинских букв и цифр, начинающиеся с буквы.

Строковые константы — последовательности строковых секций, записанных слитно. Строковые секции: 
либо последовательность символов, ограниченных апострофами, апостроф внутри строки описывается как 
два апострофа подряд, не пересекают границы строк текста, либо знак «#», за которым следует десятичная 
константа (код символа).

Пример строковой константы: «'hello'#10#13'world'» (эта строковая константа состоит из 4 строковых 
секций, однако является единым токеном).

## Лексический домен для защиты
Восьмеричные константы, как в Си: начинаются на 0 и состоят из восьмеричных цифр

# Реализация

```python
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
```

# Тестирование

Входные данные

```text
_count:=10a0
'hello'#10#13'world' abc A1B2
'it''s ok'#65
???abc
abc'hello'#10'13'
15.7
011
```

Вывод на `stdout` (если необходимо)

```shell
syntax error (1,1)
IDENT (1, 2): count
syntax error (1,7)
OCT (1, 10): 0
IDENT (1, 11): a0
STRING (2, 1): 'hello'#10#13'world'
IDENT (2, 22): abc
IDENT (2, 26): A1B2
STRING (3, 1): 'it''s ok'#65
syntax error (4,1)
IDENT (4, 4): abc
IDENT (5, 1): abc
STRING (5, 4): 'hello'#10'13'
syntax error (6,1)
OCT (7, 1): 011
```

# Вывод
В данной лабораторной работе была реализована начальная стадия анализа текста программы: чтение 
входного файла в UTF-8, последовательный просмотр символов и разбиение исходного текста на лексемы 
с вычислением их координат (строка, столбец). В соответствии с требованиями, распознавание выполняется 
cопоставлением с регулярными выражениями, а результатом работы является печать каждой найденной лексемы 
в формате «тег (координаты): значение», что позволяет явно увидеть, какие фрагменты входа относятся к 
каким доменам.

В ходе работы были описаны регулярные выражения для идентификаторов, строковых констант из нескольких 
слитно записанных секций, а также для домена защиты — восьмеричных констант в стиле С. Дополнительно 
реализована логика выбора наиболее длинного подходящего совпадения среди проверяемых доменов, что 
позволяет корректно разбирать случаи, когда разные шаблоны могут начинаться одинаково, а также 
поддерживать ситуацию, когда лексемы во входе могут быть записаны как через пробелы, так и слитно без 
противоречий.

Отдельное внимание уделено обработке ошибок: при невозможности распознать лексему на текущей позиции 
анализатор выводит сообщение вида syntax error (строка,столбец) и выполняет восстановление, пропуская 
символы до тех пор, пока снова не встретится начало пробельной последовательности или какой-либо 
лексемы. Проведённое тестирование на входных данных со слитными лексемами, многочастными строками и 
заведомо ошибочными участками показало, что анализатор корректно продолжает работу после ошибок, 
находит лексемы в разных контекстах и выдаёт ожидаемые координаты и значения, что соответствует цели 
лабораторной работы.
