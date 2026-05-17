EPSILON = 'ε'
START_SYMBOL = 'E'
TERMINALS = {'left paren', 'plus sign', 'star', 'right paren', 'n', 'EOF'}
NONTERMINALS = {'F', 'T', 'T 1', 'E 1', 'E'}
PRODUCTIONS = [('E', ['T', 'E 1']),
 ('E 1', ['plus sign', 'T', 'E 1']),
 ('E 1', []),
 ('T', ['F', 'T 1']),
 ('T 1', ['star', 'F', 'T 1']),
 ('T 1', []),
 ('F', ['n']),
 ('F', ['left paren', 'E', 'right paren'])]
FIRST = {'E': ['left paren', 'n'],
 'E 1': ['plus sign', 'ε'],
 'F': ['left paren', 'n'],
 'T': ['left paren', 'n'],
 'T 1': ['star', 'ε']}
FOLLOW = {'E': ['EOF', 'right paren'],
 'E 1': ['EOF', 'right paren'],
 'F': ['EOF', 'plus sign', 'right paren', 'star'],
 'T': ['EOF', 'plus sign', 'right paren'],
 'T 1': ['EOF', 'plus sign', 'right paren']}
PARSE_TABLE = {'E': {'left paren': ['T', 'E 1'], 'n': ['T', 'E 1']},
 'E 1': {'EOF': [], 'plus sign': ['plus sign', 'T', 'E 1'], 'right paren': []},
 'F': {'left paren': ['left paren', 'E', 'right paren'], 'n': ['n']},
 'T': {'left paren': ['F', 'T 1'], 'n': ['F', 'T 1']},
 'T 1': {'EOF': [], 'plus sign': [], 'right paren': [], 'star': ['star', 'F', 'T 1']}}
