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
