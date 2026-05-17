from pprint import pformat
from grammar_lang.model import EOF_SYMBOL, EPSILON

def sorted_dict_of_sets(mapping):
    return {key: sorted(value) for key, value in sorted(mapping.items())}

def sorted_parse_table(table):
    result = {}
    for nonterminal in sorted(table.keys()):
        result[nonterminal] = {}
        for terminal in sorted(table[nonterminal].keys()):
            result[nonterminal][terminal] = list(table[nonterminal][terminal])
    return result

def make_python_table_code(grammar, first, follow, parse_table):
    terminals = sorted(set(grammar.terminals) | {EOF_SYMBOL})
    nonterminals = sorted(grammar.nonterminals)
    productions = [(p.left, list(p.right)) for p in grammar.productions]

    lines = []
    lines.append("EPSILON = {0}".format(repr(EPSILON)))
    lines.append("START_SYMBOL = {0}".format(repr(grammar.start_symbol)))
    lines.append("TERMINALS = {0}".format(pformat(set(terminals), width=100, sort_dicts=True)))
    lines.append("NONTERMINALS = {0}".format(pformat(set(nonterminals), width=100, sort_dicts=True)))
    lines.append("PRODUCTIONS = {0}".format(pformat(productions, width=100, sort_dicts=True)))
    lines.append("FIRST = {0}".format(pformat(sorted_dict_of_sets(first), width=100, sort_dicts=True)))
    lines.append("FOLLOW = {0}".format(pformat(sorted_dict_of_sets(follow), width=100, sort_dicts=True)))
    lines.append("PARSE_TABLE = {0}".format(pformat(sorted_parse_table(parse_table), width=120, sort_dicts=True)))
    lines.append("")
    return "\n".join(lines)

def write_python_table(path, grammar, first, follow, parse_table):
    code = make_python_table_code(grammar, first, follow, parse_table)
    with open(path, "w", encoding="utf-8") as file:
        file.write(code)
