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