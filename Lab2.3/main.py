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