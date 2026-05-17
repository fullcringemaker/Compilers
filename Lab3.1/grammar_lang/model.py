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