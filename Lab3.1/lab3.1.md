% Лабораторная работа № 3.1 «Самоприменимый генератор компиляторов
  на основе предсказывающего анализа»
% 18 мая 2026 г.
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

# Грамматика на входном языке

```
tokens (KW_TOKENS), (KW_IS), (KW_START).
tokens (LPAREN), (RPAREN), (COMMA), (DOT).
tokens (IDENT), (NUMBER).
(GrammarDescription) is (TokensSection) (RulesSection) (StartSection).
(TokensSection) is (TokensDecl) (TokensSection),
(TokensSection) is .
(TokensDecl) is (KW_TOKENS) (SymbolList) (DOT).
(SymbolList) is (Symbol) (SymbolListTail).
(SymbolListTail) is (COMMA) (Symbol) (SymbolListTail),
(SymbolListTail) is .
(RulesSection) is (Rule) (RulesSection),
(RulesSection) is .
(Rule) is (Symbol) (KW_IS) (RightPart) (RuleEnd).
(RightPart) is (SymbolSequence),
(RightPart) is .
(SymbolSequence) is (Symbol) (SymbolSequenceTail).
(SymbolSequenceTail) is (Symbol) (SymbolSequenceTail),
(SymbolSequenceTail) is .
(RuleEnd) is (DOT),
(RuleEnd) is (COMMA).
(StartSection) is (KW_START) (Symbol) (DOT).
(Symbol) is (LPAREN) (Name) (RPAREN).
(Name) is (NamePart) (NameTail).
(NameTail) is (NamePart) (NameTail),
(NameTail) is .
(NamePart) is (IDENT),
(NamePart) is (NUMBER).
start (GrammarDescription).

```

# Реализация
## Генератор компиляторов

generator.py
```python
import os
import sys

from grammar_lang.lexer import LexerError, tokenize
from grammar_lang.parser import ParseError, parse_tokens
from grammar_lang.extractor import GrammarError, grammar_from_tree, precheck_start_count
from grammar_lang.first_follow import LL1ConflictError, build_parse_table, compute_first, compute_follow
from grammar_lang.codegen import write_python_table

class CommandLineError(Exception):
    pass

class GeneratorTableError(Exception):
    pass

def read_text(path):
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

def get_generated_table_path():
    return os.path.abspath(os.path.join("grammar_lang", "generated_table.py"))

def is_generating_table_for_input_language(output_path):
    current_output_path = os.path.abspath(output_path)
    generated_path = get_generated_table_path()
    current_output_path = os.path.normcase(current_output_path)
    generated_path = os.path.normcase(generated_path)
    return current_output_path == generated_path

def generated_table_exists():
    return os.path.exists(get_generated_table_path())

def load_table_module(output_path):
    if is_generating_table_for_input_language(output_path):
        from grammar_lang import handwritten_table
        return handwritten_table
    if generated_table_exists():
        try:
            from grammar_lang import generated_table
        except ImportError as error:
            raise GeneratorTableError(
                "File grammar_lang/generated_table.py exists but could not be imported."
            ) from error
        return generated_table
    from grammar_lang import handwritten_table
    return handwritten_table

def prepare_output_directory(output_path):
    directory = os.path.dirname(output_path)
    if directory != "":
        os.makedirs(directory, exist_ok=True)

def build_table(input_path, output_path):
    text = read_text(input_path)
    tokens = tokenize(text)
    precheck_start_count(tokens)
    table_module = load_table_module(output_path)
    tree = parse_tokens(tokens, table_module)
    grammar = grammar_from_tree(tree)
    first = compute_first(grammar)
    follow = compute_follow(grammar, first)
    parse_table = build_parse_table(grammar, first, follow)
    prepare_output_directory(output_path)
    write_python_table(output_path, grammar, first, follow, parse_table)

    return output_path

def parse_command_line(arguments):
    if len(arguments) != 2:
        raise CommandLineError("Input file and output file must be specified")
    input_path = arguments[0]
    output_path = arguments[1]
    if input_path.startswith("--"):
        raise CommandLineError("Unexpected option: {0}".format(input_path))
    if output_path.startswith("--"):
        raise CommandLineError("Unexpected option: {0}".format(output_path))
    return input_path, output_path

def main():
    try:
        input_path, output_path = parse_command_line(sys.argv[1:])
        generated_path = build_table(input_path, output_path)
        print("Generated table:", generated_path)
    except CommandLineError as error:
        print(error)
        sys.exit(1)
    except (OSError, GeneratorTableError, LexerError, ParseError, GrammarError, LL1ConflictError) as error:
        print(error)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

grammar_lang/model.py
```python
from dataclasses import dataclass, field

EPSILON = "ε"
EOF_SYMBOL = "EOF"

@dataclass(frozen=True)
class Coord:
    line: int
    column: int

    def __str__(self):
        return "line {0}, column {1}".format(self.line, self.column)

@dataclass(frozen=True)
class Production:
    left: str
    right: tuple
    coord: Coord

    def right_as_list(self):
        return list(self.right)

@dataclass
class Grammar:
    terminals: set
    nonterminals: set
    productions: list
    start_symbol: str
    terminal_coords: dict = field(default_factory=dict)
    nonterminal_coords: dict = field(default_factory=dict)

    def productions_by_left(self):
        result = {nonterminal: [] for nonterminal in self.nonterminals}
        for production in self.productions:
            result.setdefault(production.left, []).append(production)
        return result

    def all_terminals_for_table(self):
        return set(self.terminals) | {EOF_SYMBOL}
```

grammar_lang/lexer.py
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
```

grammar_lang/tree.py
```python
class TreeNode:
    def __init__(self, name, kind="nonterminal", value=None, coord=None):
        self.name = name
        self.kind = kind
        self.value = value
        self.coord = coord
        self.children = []

    def add_child(self, child):
        self.children.append(child)

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
    return str(text).replace("\\", "\\\\").replace('"', '\\"')

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
        lines.append('  {0} [label="{1}"];'.format(node_id, escape_dot_label(node_label(node))))
        for child in node.children:
            visit(child)
            child_id = node_ids[id(child)]
            lines.append("  {0} -> {1};".format(node_id, child_id))
        if len(node.children) >= 2:
            chain = " -> ".join(node_ids[id(child)] for child in node.children)
            lines.append("  {{ rank=same; {0} [style=invis] }}".format(chain))
    visit(root)
    lines.append("}")
    return lines

def write_dot_file(root, path):
    with open(path, "w", encoding="utf-8") as file:
        file.write("\n".join(build_dot_lines(root)))
        file.write("\n")
```

grammar_lang/parser.py
```python
from grammar_lang.tree import TreeNode

class ParseError(Exception):
    pass

class Parser:
    def __init__(self, tokens, parse_table, terminals, start_symbol):
        self.tokens = tokens
        self.position = 0
        self.parse_table = parse_table
        self.terminals = set(terminals)
        self.start_symbol = start_symbol

    def current_token(self):
        if self.position >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[self.position]

    def current_symbol(self):
        return self.current_token().type

    def parse(self):
        root = TreeNode(self.start_symbol)
        stack = [("EOF", None), (self.start_symbol, root)]
        while stack:
            top_symbol, node = stack.pop()
            lookahead_token = self.current_token()
            lookahead_symbol = lookahead_token.type
            if top_symbol in self.terminals:
                self.match_terminal(top_symbol, node, lookahead_token)
                continue
            row = self.parse_table.get(top_symbol, {})
            production = row.get(lookahead_symbol)
            if production is None:
                raise ParseError(self.format_nonterminal_error(top_symbol, lookahead_token, row))
            if len(production) == 0:
                node.children.append(TreeNode("ε", kind="epsilon"))
                continue
            children = []
            for symbol in production:
                if symbol in self.terminals and symbol != "EOF":
                    child = TreeNode(symbol, kind="terminal")
                else:
                    child = TreeNode(symbol, kind="nonterminal")
                children.append(child)
            node.children.extend(children)
            for child in reversed(children):
                stack.append((child.name, child))
        return root

    def match_terminal(self, expected_symbol, node, lookahead_token):
        if expected_symbol != lookahead_token.type:
            raise ParseError(self.format_terminal_error(expected_symbol, lookahead_token))
        if expected_symbol == "EOF":
            return
        node.kind = "token"
        node.name = lookahead_token.type
        node.value = lookahead_token.value
        node.coord = (lookahead_token.line, lookahead_token.column)
        self.position += 1

    def format_terminal_error(self, expected, found_token):
        return "Syntax error at line {0}, column {1}: expected {2}, found {3}".format(
            found_token.line,
            found_token.column,
            expected,
            found_token.type,
        )

    def format_nonterminal_error(self, nonterminal, found_token, row):
        expected = sorted(row.keys())
        return "Syntax error at line {0}, column {1}: cannot expand {2} by lookahead {3}; expected one of {4}".format(
            found_token.line,
            found_token.column,
            nonterminal,
            found_token.type,
            expected,
        )

def parse_tokens(tokens, table_module):
    return Parser(
        tokens=tokens,
        parse_table=table_module.PARSE_TABLE,
        terminals=table_module.TERMINALS,
        start_symbol=table_module.START_SYMBOL,
    ).parse()
```

grammar_lang/extractor.py
```python
from grammar_lang.model import Coord, Grammar, Production

class GrammarError(Exception):
    pass

def error(message, coord=None):
    if coord is None:
        raise GrammarError(message)
    raise GrammarError("{0} at line {1}, column {2}".format(message, coord.line, coord.column))

def token_coord(node):
    if node.kind == "token" and node.coord is not None:
        return Coord(node.coord[0], node.coord[1])
    for child in node.children:
        result = token_coord(child)
        if result is not None:
            return result
    return None

def find_children(node, name):
    return [child for child in node.children if child.name == name]

def find_first_child(node, name):
    for child in node.children:
        if child.name == name:
            return child
    return None

def walk(node, name=None):
    if name is None or node.name == name:
        yield node
    for child in node.children:
        yield from walk(child, name)

def direct_nonterminal_children(node, name):
    return [child for child in node.children if child.name == name and child.kind == "nonterminal"]

def extract_name_parts(name_node):
    parts = []
    for child in name_node.children:
        if child.kind == "token" and child.name in {"IDENT", "NUMBER"}:
            parts.append(child.value)
        else:
            parts.extend(extract_name_parts(child))
    return parts

def extract_symbol(symbol_node):
    name_node = find_first_child(symbol_node, "Name")
    if name_node is None:
        coord = token_coord(symbol_node)
        error("invalid symbol node", coord)
    parts = extract_name_parts(name_node)
    coord = token_coord(symbol_node)
    return " ".join(parts), coord

def symbols_from_subtree(node):
    return [extract_symbol(symbol_node) for symbol_node in walk(node, "Symbol")]

def extract_tokens_decl(tokens_decl_node):
    symbol_list = find_first_child(tokens_decl_node, "SymbolList")
    if symbol_list is None:
        return []
    return symbols_from_subtree(symbol_list)

def extract_rule(rule_node):
    symbol_nodes = direct_nonterminal_children(rule_node, "Symbol")
    if not symbol_nodes:
        error("rule without left side", token_coord(rule_node))
    left, coord = extract_symbol(symbol_nodes[0])
    right_part = find_first_child(rule_node, "RightPart")
    if right_part is None:
        right = []
    else:
        right = [name for name, _ in symbols_from_subtree(right_part)]

    return left, right, coord

def precheck_start_count(tokens):
    start_tokens = [token for token in tokens if token.type == "KW_START"]
    if len(start_tokens) == 0:
        last = tokens[-1]
        error("grammar axiom is not specified", Coord(last.line, last.column))
    if len(start_tokens) > 1:
        second = start_tokens[1]
        error("more than one grammar axiom is specified", Coord(second.line, second.column))

def grammar_from_tree(root):
    terminals = set()
    terminal_coords = {}
    productions = []
    lhs_coords = {}
    for tokens_decl in walk(root, "TokensDecl"):
        for terminal, coord in extract_tokens_decl(tokens_decl):
            if terminal in terminals:
                error("symbol '{0}' is declared twice".format(terminal), coord)
            terminals.add(terminal)
            terminal_coords[terminal] = coord
    for rule in walk(root, "Rule"):
        left, right, coord = extract_rule(rule)
        if left in terminals:
            error("terminal symbol '{0}' cannot be used in the left side of a rule".format(left), coord)
        lhs_coords.setdefault(left, coord)
        productions.append(Production(left=left, right=tuple(right), coord=coord))
    nonterminals = set(lhs_coords.keys())
    if not productions:
        error("grammar has no rules", token_coord(root))
    start_sections = list(walk(root, "StartSection"))
    if len(start_sections) == 0:
        error("grammar axiom is not specified", token_coord(root))
    if len(start_sections) > 1:
        error("more than one grammar axiom is specified", token_coord(start_sections[1]))
    start_symbol, start_coord = extract_symbol(find_first_child(start_sections[0], "Symbol"))
    if start_symbol in terminals:
        error("grammar axiom '{0}' is a terminal symbol".format(start_symbol), start_coord)
    if start_symbol not in nonterminals:
        error("grammar axiom '{0}' has no rules".format(start_symbol), start_coord)
    for production in productions:
        for symbol in production.right:
            if symbol not in terminals and symbol not in nonterminals:
                error(
                    "symbol '{0}' is used, but it is neither declared as terminal nor present in a rule left side".format(symbol),
                    production.coord,
                )
    return Grammar(
        terminals=terminals,
        nonterminals=nonterminals,
        productions=productions,
        start_symbol=start_symbol,
        terminal_coords=terminal_coords,
        nonterminal_coords=lhs_coords,
    )
```

grammar_lang/first_follow.py
```python
from grammar_lang.model import EOF_SYMBOL, EPSILON

class LL1ConflictError(Exception):
    pass

def first_of_sequence(sequence, grammar, first):
    if len(sequence) == 0:
        return {EPSILON}
    result = set()
    for symbol in sequence:
        if symbol in grammar.terminals:
            result.add(symbol)
            return result
        symbol_first = first[symbol]
        result.update(symbol_first - {EPSILON})
        if EPSILON not in symbol_first:
            return result
    result.add(EPSILON)
    return result

def compute_first(grammar):
    first = {nonterminal: set() for nonterminal in grammar.nonterminals}
    changed = True
    while changed:
        changed = False
        for production in grammar.productions:
            before = len(first[production.left])
            first[production.left].update(first_of_sequence(production.right, grammar, first))
            if len(first[production.left]) != before:
                changed = True
    return first

def compute_follow(grammar, first):
    follow = {nonterminal: set() for nonterminal in grammar.nonterminals}
    follow[grammar.start_symbol].add(EOF_SYMBOL)
    changed = True
    while changed:
        changed = False
        for production in grammar.productions:
            right = list(production.right)
            for index, symbol in enumerate(right):
                if symbol not in grammar.nonterminals:
                    continue
                tail = tuple(right[index + 1:])
                first_tail = first_of_sequence(tail, grammar, first)
                before = len(follow[symbol])
                follow[symbol].update(first_tail - {EPSILON})
                if EPSILON in first_tail:
                    follow[symbol].update(follow[production.left])
                if len(follow[symbol]) != before:
                    changed = True
    return follow

def build_parse_table(grammar, first, follow):
    table = {nonterminal: {} for nonterminal in sorted(grammar.nonterminals)}
    for production in grammar.productions:
        sequence_first = first_of_sequence(production.right, grammar, first)
        target_terminals = set(sequence_first - {EPSILON})
        if EPSILON in sequence_first:
            target_terminals.update(follow[production.left])
        for terminal in target_terminals:
            row = table[production.left]
            right = production.right_as_list()
            if terminal in row and row[terminal] != right:
                old = " ".join(row[terminal]) if row[terminal] else EPSILON
                new = " ".join(right) if right else EPSILON
                raise LL1ConflictError(
                    "LL(1) conflict at line {0}, column {1}: table[{2}][{3}] already contains {4}, cannot add {5}".format(
                        production.coord.line,
                        production.coord.column,
                        production.left,
                        terminal,
                        old,
                        new,
                    )
                )
            row[terminal] = right
    return table
```

grammar_lang/codegen.py
```python
from grammar_lang.model import EOF_SYMBOL

def format_list(values):
    if len(values) == 0:
        return "[]"
    parts = []
    for value in values:
        parts.append(repr(value))
    return "[" + ", ".join(parts) + "]" 

def format_set(values):
    if len(values) == 0:
        return "set()"
    parts = []
    for value in sorted(values):
        parts.append(repr(value))
    return "{" + ", ".join(parts) + "}"

def format_parse_table(table):
    lines = []
    lines.append("{")
    for nonterminal in sorted(table.keys()):
        lines.append("    {0}: {{".format(repr(nonterminal)))
        for terminal in sorted(table[nonterminal].keys()):
            production = table[nonterminal][terminal]
            lines.append(
                "        {0}: {1},".format(
                    repr(terminal),
                    format_list(production)
                )
            )
        lines.append("    },")
    lines.append("}")
    return "\n".join(lines)

def make_python_table_code(grammar, first, follow, parse_table):
    terminals = set(grammar.terminals)
    terminals.add(EOF_SYMBOL)
    lines = []
    lines.append("START_SYMBOL = {0}".format(repr(grammar.start_symbol)))
    lines.append("TERMINALS = {0}".format(format_set(terminals)))
    lines.append("PARSE_TABLE = {0}".format(format_parse_table(parse_table)))
    lines.append("")
    return "\n".join(lines)

def write_python_table(path, grammar, first, follow, parse_table):
    code = make_python_table_code(grammar, first, follow, parse_table)
    with open(path, "w", encoding="utf-8") as file:
        file.write(code)
```

grammar_lang/handwritten_table.py
```python
START_SYMBOL = "GrammarDescription"

TERMINALS = {
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
}

NONTERMINALS = {
    "GrammarDescription",
    "TokensSection",
    "TokensDecl",
    "SymbolList",
    "SymbolListTail",
    "RulesSection",
    "Rule",
    "RightPart",
    "SymbolSequence",
    "SymbolSequenceTail",
    "RuleEnd",
    "StartSection",
    "Symbol",
    "Name",
    "NameTail",
    "NamePart",
}

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
```

## Калькулятор
calculator/main.py
```python
import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from calculator.calc_lexer import CalcLexerError, tokenize
from calculator.evaluator import EvaluationError, evaluate
from calculator.table_loader import TableLoadError, load_table
from grammar_lang.parser import ParseError, parse_tokens
from grammar_lang.tree import print_tree, write_dot_file

class CommandLineError(Exception):
    pass

def parse_command_line(arguments):
    expression = None
    show_tree = False
    dot_path = None
    index = 0
    while index < len(arguments):
        argument = arguments[index]
        if argument == "--tree":
            show_tree = True
            index += 1
        elif argument == "--dot":
            if index + 1 >= len(arguments):
                raise CommandLineError("Option --dot requires a file path")
            dot_path = arguments[index + 1]
            index += 2
        elif argument.startswith("--"):
            raise CommandLineError("Unknown option: {0}".format(argument))
        elif expression is None:
            expression = argument
            index += 1
        else:
            raise CommandLineError("Unexpected argument: {0}".format(argument))
    if expression is None:
        raise CommandLineError("Expression must be specified")
    return expression, show_tree, dot_path

def main():
    try:
        expression, show_tree, dot_path = parse_command_line(sys.argv[1:])
        table_module = load_table()
        tokens = tokenize(expression)
        root = parse_tokens(tokens, table_module)
        result = evaluate(root)
        if show_tree:
            print_tree(root)
        if dot_path is not None:
            write_dot_file(root, dot_path)
        print(result)
    except CommandLineError as error:
        print(error)
        sys.exit(1)
    except (TableLoadError, CalcLexerError, ParseError, EvaluationError) as error:
        print(error)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

calculator/calc_lexer.py
```python
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
```

calculator/evaluator.py
```python
class EvaluationError(Exception):
    pass

def child(node, index):
    try:
        return node.children[index]
    except IndexError:
        raise EvaluationError("invalid parse tree near {0}".format(node.name))

def is_epsilon(node):
    return len(node.children) == 1 and node.children[0].kind == "epsilon"

def evaluate(root):
    if root.name != "E":
        raise EvaluationError("calculator parse tree root must be E")
    return eval_E(root)

def eval_E(node):
    value = eval_T(child(node, 0))
    return eval_E1(child(node, 1), value)

def eval_E1(node, accumulated):
    if is_epsilon(node):
        return accumulated
    term_value = eval_T(child(node, 1))
    return eval_E1(child(node, 2), accumulated + term_value)

def eval_T(node):
    value = eval_F(child(node, 0))
    return eval_T1(child(node, 1), value)

def eval_T1(node, accumulated):
    if is_epsilon(node):
        return accumulated
    factor_value = eval_F(child(node, 1))
    return eval_T1(child(node, 2), accumulated * factor_value)

def eval_F(node):
    first = child(node, 0)
    if first.name == "n":
        return first.value
    return eval_E(child(node, 1))
```

calculator/table_loader.py
```python
class TableLoadError(Exception):
    pass

def load_table():
    try:
        from output import calculator_table
    except ImportError as error:
        raise TableLoadError(
            "Table file output/calculator_table.py was not found. "
            "Generate it first with generator.py"
        ) from error
    if not hasattr(calculator_table, "PARSE_TABLE"):
        raise TableLoadError("File output/calculator_table.py does not contain PARSE_TABLE")

    return calculator_table
```

# Тестирование
## Генератор компиляторов

### Таблица для калькулятора
output/calculator_table.py
```python
START_SYMBOL = 'E'
TERMINALS = {'EOF', 'left paren', 'n', 'plus sign', 'right paren', 'star'}
PARSE_TABLE = {
    'E': {
        'left paren': ['T', 'E 1'],
        'n': ['T', 'E 1'],
    },
    'E 1': {
        'EOF': [],
        'plus sign': ['plus sign', 'T', 'E 1'],
        'right paren': [],
    },
    'F': {
        'left paren': ['left paren', 'E', 'right paren'],
        'n': ['n'],
    },
    'T': {
        'left paren': ['F', 'T 1'],
        'n': ['F', 'T 1'],
    },
    'T 1': {
        'EOF': [],
        'plus sign': [],
        'right paren': [],
        'star': ['star', 'F', 'T 1'],
    },
}
```

### Таблица для собственной грамматики
grammar_lang/generated_table.py
```
START_SYMBOL = 'GrammarDescription'
TERMINALS = {'COMMA', 'DOT', 'EOF', 'IDENT', 'KW_IS', 'KW_START', 'KW_TOKENS', 'LPAREN', 'NUMBER', 'RPAREN'}
PARSE_TABLE = {
    'GrammarDescription': {
        'KW_START': ['TokensSection', 'RulesSection', 'StartSection'],
        'KW_TOKENS': ['TokensSection', 'RulesSection', 'StartSection'],
        'LPAREN': ['TokensSection', 'RulesSection', 'StartSection'],
    },
    'Name': {
        'IDENT': ['NamePart', 'NameTail'],
        'NUMBER': ['NamePart', 'NameTail'],
    },
    'NamePart': {
        'IDENT': ['IDENT'],
        'NUMBER': ['NUMBER'],
    },
    'NameTail': {
        'IDENT': ['NamePart', 'NameTail'],
        'NUMBER': ['NamePart', 'NameTail'],
        'RPAREN': [],
    },
    'RightPart': {
        'COMMA': [],
        'DOT': [],
        'LPAREN': ['SymbolSequence'],
    },
    'Rule': {
        'LPAREN': ['Symbol', 'KW_IS', 'RightPart', 'RuleEnd'],
    },
    'RuleEnd': {
        'COMMA': ['COMMA'],
        'DOT': ['DOT'],
    },
    'RulesSection': {
        'KW_START': [],
        'LPAREN': ['Rule', 'RulesSection'],
    },
    'StartSection': {
        'KW_START': ['KW_START', 'Symbol', 'DOT'],
    },
    'Symbol': {
        'LPAREN': ['LPAREN', 'Name', 'RPAREN'],
    },
    'SymbolList': {
        'LPAREN': ['Symbol', 'SymbolListTail'],
    },
    'SymbolListTail': {
        'COMMA': ['COMMA', 'Symbol', 'SymbolListTail'],
        'DOT': [],
    },
    'SymbolSequence': {
        'LPAREN': ['Symbol', 'SymbolSequenceTail'],
    },
    'SymbolSequenceTail': {
        'COMMA': [],
        'DOT': [],
        'LPAREN': ['Symbol', 'SymbolSequenceTail'],
    },
    'TokensDecl': {
        'KW_TOKENS': ['KW_TOKENS', 'SymbolList', 'DOT'],
    },
    'TokensSection': {
        'KW_START': [],
        'KW_TOKENS': ['TokensDecl', 'TokensSection'],
        'LPAREN': [],
    },
}
```

## Калькулятор
Входные данные
```shell
((12+3)*(4+5*6)+7)*(8+2*3)+9
```

Вывод на `stdout`
```shell
7247
```

# Вывод
В данной лабораторной работе был разработан самоприменимый генератор компиляторов на основе предсказывающего анализа, который по описанию грамматики строит таблицу разбора и тем самым позволяет автоматически получать синтаксический анализатор для заданного входного языка. По условиям требовалось организовать полный путь от исходного текста грамматики до структур данных, пригодных для разбора, а затем использовать результат для порождения дерева вывода и дальнейшего применения в отдельных программах.

Далее была реализована автоматическая генерация таблицы разбора по дереву разбора описания грамматики и выполнена проверка корректности самой грамматики на набор обязательных условий. Были предусмотрены сообщения об ошибках с координатами, что позволяет локализовать проблему в исходном тексте грамматики без усложнения механизма восстановления. Такой контроль обеспечивает надёжность генерации и защищает от ситуаций, когда построенная таблица не соответствует требованиям предсказывающего разбора.

На завершающем этапе работоспособность генератора была подтверждена на примере отдельной программы калькулятора, где грамматика задаёт правила вычисления выражений, а построенная таблица используется для разбора входной строки. После этого была выполнена раскрутка, при которой язык описания грамматик был записан на самом себе, а вручную заданная таблица была заменена на сгенерированную, что демонстрирует самоприменимость подхода. В результате получена связка, позволяющая описывать грамматики, автоматически строить таблицы разбора и применять их в независимых прикладных анализаторах.
