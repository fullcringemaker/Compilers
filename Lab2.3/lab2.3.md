% Лабораторная работа № 2.3 «Синтаксический анализатор на основе
  предсказывающего анализа»
% 22 апреля 2026 г.
% Дмитрий Трофименко, ИУ9-62Б

# Цель работы
Целью данной работы является изучение алгоритма построения таблиц предсказывающего анализатора.

# Индивидуальный вариант
```
tokens (plus sign), (star), (n).
tokens (left paren), (right paren).
(E)   is (T) (E 1).
(E 1) is (plus sign) (T) (E 1),
(E 1) is .
(T)   is (F) (T 1).
(T 1) is (star) (F) (T 1),
(T 1) is .
(F)   is (n),
(F)   is (left paren) (E) (right paren).
(* аксиома *)
start (E).
```

# Реализация

## Неформальное описание синтаксиса входного языка
В качестве входного языка выступает язык представления правил грамматики. С его помощью задаются 
объявления терминальных символов, правила грамматики и аксиома. Полное описание грамматики состоит 
из трёх основных частей: списка объявлений терминалов, списка правил и объявления начального нетерминала.

```text
GrammarDescription ::= TokensSection RulesSection StartSection
```

Нетреминал GrammarDescription описывает всю программу целиком. Сначала в ней идёт секция объявлений 
терминалов, затем секция правил грамматики, после чего записывается объявление аксиомы.

Секция объявлений терминалов может содержать одно или несколько объявлений tokens, а также может 
отсутствовать.

```text
TokensSection ::= TokensDecl TokensSection | ε
```

Каждое объявление терминалов начинается с ключевого слова tokens, после которого следует список 
символов, а затем точка.

```text
TokensDecl ::= tokens SymbolList .
```

Список символов состоит как минимум из одного символа. После первого символа могут следовать другие 
символы, отделённые запятыми.

```text
SymbolList ::= Symbol SymbolListTail
```

Продолжение списка символов либо начинается с запятой и ещё одного символа, после чего список может 
продолжаться дальше, либо список на этом заканчивается.

```text
SymbolListTail ::= , Symbol SymbolListTail | ε
```

После секции объявлений терминалов записывается секция правил грамматики. Она состоит из одного или 
нескольких правил, но в формальной записи допускается и пустой вариант.

```text
RulesSection ::= Rule RulesSection | ε
```

Каждое правило состоит из символа в левой части, ключевого слова is, правой части и завершающего знака. 
В зависимости от записи правило может оканчиваться точкой или запятой.

```text
Rule ::= Symbol is RightPart RuleEnd
```

Правая часть правила может содержать последовательность символов или быть пустой. Пустая правая часть 
соответствует эпсилон-правилу.

```text
RightPart ::= SymbolSequence | ε
```

Последовательность символов начинается с одного символа, после которого может следовать продолжение 
последовательности.

```text
SymbolSequence ::= Symbol SymbolSequenceTail
```

Нетреминал SymbolSequenceTail описывает продолжение последовательности символов. После первого символа 
может идти ещё один символ и дальнейшее продолжение, либо последовательность может завершиться.

```text
SymbolSequenceTail ::= Symbol SymbolSequenceTail | ε
```

Завершение правила может задаваться либо точкой, либо запятой. Точка обычно завершает всю группу правил 
или отдельную конструкцию, а запятая используется там, где после текущего правила следует ещё одно 
правило того же нетерминала.

```text
RuleEnd ::= . | ,
```

После всех правил указывается аксиома. Объявление аксиомы начинается с ключевого слова start, после 
которого идёт один символ, а затем точка.

```text
StartSection ::= start Symbol .
```

Символ языка всегда записывается в круглых скобках. Внутри скобок находится имя символа.

```text
Symbol ::= ( Name )
```

Имя символа состоит из одной или нескольких частей. Это позволяет записывать как простые имена вроде E 
или n, так и составные имена вроде plus sign, left paren или E 1.

```text
Name ::= NamePart NameTail
```

Продолжение имени может содержать ещё одну часть имени и затем снова продолжение, либо имя может 
завершиться.

```text
NameTail ::= NamePart NameTail | ε
```

Одна часть имени представляет собой либо идентификатор, либо число.

```text
NamePart ::= IDENT | NUMBER
```

Таким образом, имеем следующие элементы входного языка:

- Терминалы: `tokens`, `is`, `start`, `(`, `)`, `,`, `.`, `IDENT`, `NUMBER`.
- Нетерминалы: `GrammarDescription`, `TokensSection`, `TokensDecl`, `SymbolList`, `SymbolListTail`, 
`RulesSection`, `Rule`, `RightPart`, `SymbolSequence`, `RuleEnd`, `StartSection`, `Symbol`, `Name`, 
`NameTail`, `NamePart`.
- Ключевые слова: `tokens`, `is`, `start`.
- Знаки пунктуации: `(`, `)`, `,`, `.`
- Идентификатор: последовательность букв, используемая как часть имени символа.
- Число: последовательность цифр, используемая как часть имени символа.

## Лексическая структура
```
KW_TOKENS    ::= tokens
KW_IS        ::= is
KW_START     ::= start
LPAREN       ::= \(
RPAREN       ::= \)
COMMA        ::= ,
DOT          ::= \.
IDENT        ::= [A-Za-z]+
NUMBER       ::= [0-9]+
COMMENT      ::= \(\*[\s\S]*?\*\)
WHITESPACE   ::= [ \t\r\n]+
```

## Грамматика языка
```
GrammarDescription ::= TokensSection RulesSection StartSection
TokensSection ::= TokensDecl TokensSection | ε
TokensDecl ::= tokens SymbolList .
SymbolList ::= Symbol SymbolListTail
SymbolListTail ::= , Symbol SymbolListTail | ε
RulesSection ::= Rule RulesSection | ε
Rule ::= Symbol is RightPart RuleEnd
RightPart ::= SymbolSequence | ε
SymbolSequence ::= Symbol SymbolSequenceTail
SymbolSequenceTail ::= Symbol SymbolSequenceTail | ε
RuleEnd ::= . | ,
StartSection ::= start Symbol .
Symbol ::= ( Name )
Name ::= NamePart NameTail
NameTail ::= NamePart NameTail | ε
NamePart ::= IDENT | NUMBER
```

## Программная реализация

main.py
```
import sys
from lexer import tokenize, LexerError

class ParseError(Exception):
    pass

class TreeNode:
    def __init__(self, name, kind="nonterminal", value=None):
        self.name = name
        self.kind = kind
        self.value = value
        self.children = []

TERMINALS = set([
    "KW_TOKENS",
    "KW_IS",
    "KW_START",
    "LPAREN",
    "RPAREN",
    "COMMA",
    "DOT",
    "IDENT",
    "NUMBER",
    "EOF",
])

PARSE_TABLE = {
    "GrammarDescription": {
        "KW_TOKENS": ["TokensSection", "RulesSection", "StartSection"],
        "LPAREN": ["TokensSection", "RulesSection", "StartSection"],
        "KW_START": ["TokensSection", "RulesSection", "StartSection"],
    },
    "TokensSection": {
        "KW_TOKENS": ["TokensDecl", "TokensSection"],
        "LPAREN": [],
        "KW_START": [],
    },
    "TokensDecl": {
        "KW_TOKENS": ["KW_TOKENS", "SymbolList", "DOT"],
    },
    "SymbolList": {
        "LPAREN": ["Symbol", "SymbolListTail"],
    },
    "SymbolListTail": {
        "COMMA": ["COMMA", "Symbol", "SymbolListTail"],
        "DOT": [],
    },
    "RulesSection": {
        "LPAREN": ["Rule", "RulesSection"],
        "KW_START": [],
    },
    "Rule": {
        "LPAREN": ["Symbol", "KW_IS", "RightPart", "RuleEnd"],
    },
    "RightPart": {
        "LPAREN": ["SymbolSequence"],
        "DOT": [],
        "COMMA": [],
    },
    "SymbolSequence": {
        "LPAREN": ["Symbol", "SymbolSequenceTail"],
    },
    "SymbolSequenceTail": {
        "LPAREN": ["Symbol", "SymbolSequenceTail"],
        "DOT": [],
        "COMMA": [],
    },
    "RuleEnd": {
        "DOT": ["DOT"],
        "COMMA": ["COMMA"],
    },
    "StartSection": {
        "KW_START": ["KW_START", "Symbol", "DOT"],
    },
    "Symbol": {
        "LPAREN": ["LPAREN", "Name", "RPAREN"],
    },
    "Name": {
        "IDENT": ["NamePart", "NameTail"],
        "NUMBER": ["NamePart", "NameTail"],
    },
    "NameTail": {
        "IDENT": ["NamePart", "NameTail"],
        "NUMBER": ["NamePart", "NameTail"],
        "RPAREN": [],
    },
    "NamePart": {
        "IDENT": ["IDENT"],
        "NUMBER": ["NUMBER"],
    },
}

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.position = 0

    def current_token(self):
        return self.tokens[self.position]

    def current_symbol(self):
        return self.current_token().type

    def parse(self):
        root = TreeNode("GrammarDescription")
        stack = [("EOF", None), ("GrammarDescription", root)]

        while stack:
            top_symbol, node = stack.pop()
            lookahead_token = self.current_token()
            lookahead_symbol = self.current_symbol()

            if top_symbol in TERMINALS:
                self.match_terminal(top_symbol, node, lookahead_token, lookahead_symbol)
                continue

            row = PARSE_TABLE.get(top_symbol, {})
            production = row.get(lookahead_symbol)

            if production is None:
                raise ParseError(self.format_nonterminal_error(top_symbol, lookahead_token, row))

            if len(production) == 0:
                node.children.append(TreeNode("ε", kind="epsilon"))
                continue

            children = []
            for symbol in production:
                if symbol in TERMINALS and symbol != "EOF":
                    child = TreeNode(symbol, kind="terminal")
                else:
                    child = TreeNode(symbol, kind="nonterminal")
                children.append(child)

            node.children.extend(children)

            for child in reversed(children):
                stack.append((child.name, child))
        return root

    def match_terminal(self, expected_symbol, node, lookahead_token, lookahead_symbol):
        if expected_symbol == "EOF":
            if lookahead_symbol != "EOF":
                raise ParseError(self.format_terminal_error(expected_symbol, lookahead_token))
            return

        if expected_symbol != lookahead_symbol:
            raise ParseError(self.format_terminal_error(expected_symbol, lookahead_token))

        node.kind = "token"
        node.name = lookahead_token.type
        node.value = lookahead_token.value
        node.coord = (lookahead_token.line, lookahead_token.column)
        self.position += 1

    def format_terminal_error(self, expected, found_token):
        return "Syntax error at line {0}, column {1}".format(
            found_token.line,
            found_token.column
        )

    def format_nonterminal_error(self, nonterminal, found_token, row):
        return "Syntax error at line {0}, column {1}".format(
            found_token.line,
            found_token.column
        )

def print_tree(node, indent=0):
    prefix = "  " * indent

    if node.kind == "token":
        print(prefix + "{0}: {1}".format(node.name, node.value))
    elif node.kind == "epsilon":
        print(prefix + "ε")
    else:
        print(prefix + node.name)

    for child in node.children:
        print_tree(child, indent + 1)

def escape_dot_label(text):
    return text.replace("\\", "\\\\").replace('"', '\\"')

def node_label(node):
    if node.kind == "token":
        return "{0}: {1}".format(node.name, node.value)
    return node.name

def build_dot_lines(root):
    lines = ["digraph ParseTree {"]
    lines.append("  rankdir=TB;")
    lines.append("  node [shape=box];")

    node_ids = {}
    counter = [0]

    def visit(node):
        node_id = "n{0}".format(counter[0])
        counter[0] += 1
        node_ids[id(node)] = node_id

        lines.append(
            '  {0} [label="{1}"];'.format(node_id, escape_dot_label(node_label(node)))
        )

        children = node.children

        for child in children:
            visit(child)
            child_id = node_ids[id(child)]
            lines.append("  {0} -> {1};".format(node_id, child_id))

        if len(children) >= 2:
            chain = " -> ".join(node_ids[id(child)] for child in children)
            lines.append("  {{ rank=same; {0} [style=invis] }}".format(chain))

    visit(root)
    lines.append("}")
    return lines

def write_dot_file(root, path):
    dot_code = "\n".join(build_dot_lines(root)) + "\n"
    with open(path, "w", encoding="utf-8") as file:
        file.write(dot_code)

def read_text(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

def main():
    input_path = "input.txt"
    output_path = "tree.dot"

    if len(sys.argv) > 1:
        input_path = sys.argv[1]
    if len(sys.argv) > 2:
        output_path = sys.argv[2]

    try:
        text = read_text(input_path)
        tokens = tokenize(text)
        parser = Parser(tokens)
        tree = parser.parse()

        write_dot_file(tree, output_path)
        print("Текстовое представление дерева:")
        print_tree(tree)
    except FileNotFoundError:
        print("Не удалось открыть файл: {0}".format(input_path))
    except LexerError as error:
        print(error)
    except ParseError as error:
        print(error)

if __name__ == "__main__":
    main()
```

lexer.py
```python
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
    ("IDENT", r"[A-Za-z]+"),
    ("NUMBER", r"[0-9]+"),
]

MASTER_REGEX = re.compile(
    "|".join("(?P<{0}>{1})".format(name, pattern) for name, pattern in TOKEN_SPECS)
)

SKIP_TYPES = set(["COMMENT", "WHITESPACE"])

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
                    line,
                    column,
                    repr(bad_char)
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

```

# Тестирование

Входные данные

```text
tokens (plus sign), (star), (n).
tokens (left paren), (right paren).
(E)   is (T) (E 1).
(E 1) is (plus sign) (T) (E 1),
(E 1) is .
(T)   is (F) (T 1).
(T 1) is (star) (F) (T 1),
(T 1) is .
(F)   is (n),
(F)   is (left paren) (E) (right paren).
(* аксиома *)
start (E).
```

Вывод на `stdout`

```shell
Текстовое представление дерева:
GrammarDescription
  TokensSection
    TokensDecl
      KW_TOKENS: tokens
      SymbolList
        Symbol
          LPAREN: (
          Name
            NamePart
              IDENT: plus
            NameTail
              NamePart
                IDENT: sign
              NameTail
                ε
          RPAREN: )
        SymbolListTail
          COMMA: ,
          Symbol
            LPAREN: (
            Name
              NamePart
                IDENT: star
              NameTail
                ε
            RPAREN: )
          SymbolListTail
            COMMA: ,
            Symbol
              LPAREN: (
              Name
                NamePart
                  IDENT: n
                NameTail
                  ε
              RPAREN: )
            SymbolListTail
              ε
      DOT: .
    TokensSection
      TokensDecl
        KW_TOKENS: tokens
        SymbolList
          Symbol
            LPAREN: (
            Name
              NamePart
                IDENT: left
              NameTail
                NamePart
                  IDENT: paren
                NameTail
                  ε
            RPAREN: )
          SymbolListTail
            COMMA: ,
            Symbol
              LPAREN: (
              Name
                NamePart
                  IDENT: right
                NameTail
                  NamePart
                    IDENT: paren
                  NameTail
                    ε
              RPAREN: )
            SymbolListTail
              ε
        DOT: .
      TokensSection
        ε
  RulesSection
    Rule
      Symbol
        LPAREN: (
        Name
          NamePart
            IDENT: E
          NameTail
            ε
        RPAREN: )
      KW_IS: is
      RightPart
        SymbolSequence
          Symbol
            LPAREN: (
            Name
              NamePart
                IDENT: T
              NameTail
                ε
            RPAREN: )
          SymbolSequenceTail
            Symbol
              LPAREN: (
              Name
                NamePart
                  IDENT: E
                NameTail
                  NamePart
                    NUMBER: 1
                  NameTail
                    ε
              RPAREN: )
            SymbolSequenceTail
              ε
      RuleEnd
        DOT: .
    RulesSection
      Rule
        Symbol
          LPAREN: (
          Name
            NamePart
              IDENT: E
            NameTail
              NamePart
                NUMBER: 1
              NameTail
                ε
          RPAREN: )
        KW_IS: is
        RightPart
          SymbolSequence
            Symbol
              LPAREN: (
              Name
                NamePart
                  IDENT: plus
                NameTail
                  NamePart
                    IDENT: sign
                  NameTail
                    ε
              RPAREN: )
            SymbolSequenceTail
              Symbol
                LPAREN: (
                Name
                  NamePart
                    IDENT: T
                  NameTail
                    ε
                RPAREN: )
              SymbolSequenceTail
                Symbol
                  LPAREN: (
                  Name
                    NamePart
                      IDENT: E
                    NameTail
                      NamePart
                        NUMBER: 1
                      NameTail
                        ε
                  RPAREN: )
                SymbolSequenceTail
                  ε
        RuleEnd
          COMMA: ,
      RulesSection
        Rule
          Symbol
            LPAREN: (
            Name
              NamePart
                IDENT: E
              NameTail
                NamePart
                  NUMBER: 1
                NameTail
                  ε
            RPAREN: )
          KW_IS: is
          RightPart
            ε
          RuleEnd
            DOT: .
        RulesSection
          Rule
            Symbol
              LPAREN: (
              Name
                NamePart
                  IDENT: T
                NameTail
                  ε
              RPAREN: )
            KW_IS: is
            RightPart
              SymbolSequence
                Symbol
                  LPAREN: (
                  Name
                    NamePart
                      IDENT: F
                    NameTail
                      ε
                  RPAREN: )
                SymbolSequenceTail
                  Symbol
                    LPAREN: (
                    Name
                      NamePart
                        IDENT: T
                      NameTail
                        NamePart
                          NUMBER: 1
                        NameTail
                          ε
                    RPAREN: )
                  SymbolSequenceTail
                    ε
            RuleEnd
              DOT: .
          RulesSection
            Rule
              Symbol
                LPAREN: (
                Name
                  NamePart
                    IDENT: T
                  NameTail
                    NamePart
                      NUMBER: 1
                    NameTail
                      ε
                RPAREN: )
              KW_IS: is
              RightPart
                SymbolSequence
                  Symbol
                    LPAREN: (
                    Name
                      NamePart
                        IDENT: star
                      NameTail
                        ε
                    RPAREN: )
                  SymbolSequenceTail
                    Symbol
                      LPAREN: (
                      Name
                        NamePart
                          IDENT: F
                        NameTail
                          ε
                      RPAREN: )
                    SymbolSequenceTail
                      Symbol
                        LPAREN: (
                        Name
                          NamePart
                            IDENT: T
                          NameTail
                            NamePart
                              NUMBER: 1
                            NameTail
                              ε
                        RPAREN: )
                      SymbolSequenceTail
                        ε
              RuleEnd
                COMMA: ,
            RulesSection
              Rule
                Symbol
                  LPAREN: (
                  Name
                    NamePart
                      IDENT: T
                    NameTail
                      NamePart
                        NUMBER: 1
                      NameTail
                        ε
                  RPAREN: )
                KW_IS: is
                RightPart
                  ε
                RuleEnd
                  DOT: .
              RulesSection
                Rule
                  Symbol
                    LPAREN: (
                    Name
                      NamePart
                        IDENT: F
                      NameTail
                        ε
                    RPAREN: )
                  KW_IS: is
                  RightPart
                    SymbolSequence
                      Symbol
                        LPAREN: (
                        Name
                          NamePart
                            IDENT: n
                          NameTail
                            ε
                        RPAREN: )
                      SymbolSequenceTail
                        ε
                  RuleEnd
                    COMMA: ,
                RulesSection
                  Rule
                    Symbol
                      LPAREN: (
                      Name
                        NamePart
                          IDENT: F
                        NameTail
                          ε
                      RPAREN: )
                    KW_IS: is
                    RightPart
                      SymbolSequence
                        Symbol
                          LPAREN: (
                          Name
                            NamePart
                              IDENT: left
                            NameTail
                              NamePart
                                IDENT: paren
                              NameTail
                                ε
                          RPAREN: )
                        SymbolSequenceTail
                          Symbol
                            LPAREN: (
                            Name
                              NamePart
                                IDENT: E
                              NameTail
                                ε
                            RPAREN: )
                          SymbolSequenceTail
                            Symbol
                              LPAREN: (
                              Name
                                NamePart
                                  IDENT: right
                                NameTail
                                  NamePart
                                    IDENT: paren
                                  NameTail
                                    ε
                              RPAREN: )
                            SymbolSequenceTail
                              ε
                    RuleEnd
                      DOT: .
                  RulesSection
                    ε
  StartSection
    KW_START: start
    Symbol
      LPAREN: (
      Name
        NamePart
          IDENT: E
        NameTail
          ε
      RPAREN: )
    DOT: .
```

# Вывод
В данной лабораторной работе был разработан синтаксический анализатор на основе предсказывающего 
анализа, который по входному тексту строит дерево вывода и тем самым фиксирует структуру разобранной 
программы. В рамках задания требовалось восстановить описание входного языка по образцу, организовать 
разбор с использованием таблицы предсказывающего разбора и получить результат в виде дерева.

В ходе выполнения работы были сформулированы лексическая структура и грамматика языка описания правил, 
включающего объявления терминалов, набор правил и указание начального символа. После этого был 
реализован лексический анализ, обеспечивающий выделение ключевых слов, пунктуации и компонентов имён 
символов с вычислением координат, а также пропуск пробельных фрагментов и комментариев. Такой этап 
подготовки гарантирует, что синтаксический разбор получает корректный поток токенов и может однозначно 
выбирать правила по текущему символу просмотра.

Затем была вручную составлена таблица предсказывающего разбора и реализован алгоритм, который управляет 
процессом раскрытия нетерминалов по этой таблице, включая обработку пустых правил и проверку 
соответствия терминалов входным токенам. Полученное дерево вывода выводится в текстовом виде и может 
быть сохранено в формате для визуализации, что упрощает проверку правильности работы анализатора. 
Тестирование на примере, содержащем все основные конструкции входного языка, показало, что разбор 
выполняется корректно и приводит к построению ожидаемой иерархии элементов описания грамматики.
