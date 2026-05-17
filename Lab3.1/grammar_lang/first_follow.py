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
