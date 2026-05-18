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
