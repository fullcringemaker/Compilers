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
