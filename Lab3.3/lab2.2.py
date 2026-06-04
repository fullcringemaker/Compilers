import abc
import enum
import typing
from dataclasses import dataclass
import parser_edsl as pe
import re
from pprint import pprint
import sys

# ---------- Узлы абстрактного синтаксического дерева ----------

# Type → INT | CHAR | BOOL
class Type(enum.Enum):
    Int = 'int'
    Char = 'char'
    Bool = 'bool'

# Type → Type ARRAY
@dataclass
class ArrayType:
    type: typing.Any

# Parameter → VarName Type
@dataclass
class Parameter:
    name: str
    type: typing.Any

class Statement(abc.ABC):
    pass

class Expr(abc.ABC):
    pass

# Program → Function*
@dataclass
class Program:
    functions: list[typing.Any]

# Function → FuncName Parameters ReturnType? Statements
@dataclass
class FunctionDef:
    name: str
    params: list[Parameter]
    return_type: typing.Optional[typing.Any]
    body: list[Statement]

# DeclItem → VarName Expr?
@dataclass
class DeclItem:
    name: str
    expr: typing.Optional[Expr]

# Statement → DeclStatement
# DeclStatement → Type DeclItem+
@dataclass
class DeclStatement(Statement):
    type: typing.Any
    items: list[DeclItem]

# Statement → AssignStatement
# AssignStatement → LValue Expr
@dataclass
class AssignStatement(Statement):
    variable: Expr
    expr: Expr

# Expr → FuncCallExpr
# FuncCallExpr → FuncName Arguments
@dataclass
class CallExpr(Expr):
    func: str
    args: list[Expr]

# Statement → CallStatement
@dataclass
class CallStatement(Statement):
    call: CallExpr

# Branch → Expr Statements
@dataclass
class IfBranch:
    condition: Expr
    body: list[Statement]

# Statement → IfStatement
# IfStatement → Branch+ ElseBranch?
@dataclass
class IfStatement(Statement):
    branches: list[IfBranch]
    else_body: list[Statement]

# Statement → WhileStatement
# WhileStatement → Expr Statements
@dataclass
class WhileStatement(Statement):
    condition: Expr
    body: list[Statement]

# Statement → ForStatement
# ForStatement → ForTarget Expr Expr? Statements
@dataclass
class ForStatement(Statement):
    type: typing.Optional[typing.Any]
    variable: str
    start: Expr
    end: Expr
    step: Expr
    body: list[Statement]

# Statement → DoWhileStatement
# DoWhileStatement → Statements Expr
@dataclass
class DoWhileStatement(Statement):
    body: list[Statement]
    condition: Expr

# Statement → ReturnStatement
# ReturnStatement → Expr?
@dataclass
class ReturnStatement(Statement):
    expr: typing.Optional[Expr]

# Statement → AssertStatement
# AssertStatement → Expr
@dataclass
class AssertStatement(Statement):
    condition: Expr

# Expr → VariableExpr
@dataclass
class VariableExpr(Expr):
    varname: str

# Expr → ConstExpr
# ConstExpr → INT_CONST | CHAR_CONST | STRING_CONST | T | F | NULL
@dataclass
class ConstExpr(Expr):
    value: typing.Any
    type: typing.Any

# Expr → ArrayAccessExpr
# ArrayAccessExpr → Expr Expr
@dataclass
class IndexExpr(Expr):
    array: Expr
    index: Expr

# Expr → NewArrayExpr
# NewArrayExpr → Type Expr
@dataclass
class NewExpr(Expr):
    type: typing.Any
    size: Expr

# Expr → Expr BinOp Expr
# BinOp → ** | * | / | MOD | + | - | = | <> | < | > | <= | >= | AND | OR | XOR
@dataclass
class BinOpExpr(Expr):
    left: Expr
    op: str
    right: Expr

# Expr → UnOp Expr
# UnOp → - | NOT
@dataclass
class UnOpExpr(Expr):
    op: str
    expr: Expr

@dataclass
class NoReturnType:
    pass

# # ---------- Terminals ----------

IDENT = pe.Terminal('IDENT', '[A-Za-z][A-Za-z0-9_]*', str)
FUNCNAME = pe.Terminal('FUNCNAME', '[A-Z][A-Za-z0-9_]*(?=\\s*\\()', str)
INT_CONST = pe.Terminal(
    'INT_CONST',
    '(\\{[0-9]+\\}[0-9A-Za-z]+|[0-9]+)',
    str,
    priority=7
)
CHAR_CONST = pe.Terminal(
    'CHAR_CONST',
    "'([^'\\n]|'')'|\\#[A-Z]+|\\#\\{[0-9A-Fa-f]+\\}",
    str,
    priority=7
)
STRING_CONST = pe.Terminal(
    'STRING_CONST',
    '("([^"\\n])*"|\\$QUOT|\\$[A-Z]+|\\$\\{[0-9A-Fa-f]+\\})([ \\t\\r\\n]+("([^"\\n])*"|\\$QUOT|\\$[A-Z]+|\\$\\{[0-9A-Fa-f]+\\}))*',
    str,
    priority=7
)

def make_keyword(word):
    return pe.Terminal(
        word.upper(),
        word,
        lambda _: None,
        re_flags=re.IGNORECASE,
        priority=10
    )

KW_AND = make_keyword('and')
KW_ELSE = make_keyword('else')
KW_NEW = make_keyword('new')
KW_THEN = make_keyword('then')

KW_ARRAY = make_keyword('array')
KW_ELSIF = make_keyword('elsif')
KW_NOT = make_keyword('not')
KW_TO = make_keyword('to')

KW_ASSERT = make_keyword('assert')
KW_END = make_keyword('end')
KW_NULL = make_keyword('NULL')
KW_WHILE = make_keyword('while')

KW_BOOL = make_keyword('bool')
KW_F = make_keyword('F')
KW_OR = make_keyword('or')
KW_XOR = make_keyword('xor')

KW_CHAR = make_keyword('char')
KW_IF = make_keyword('if')
KW_RETURN = make_keyword('return')

KW_DEFINE = make_keyword('define')
KW_INT = make_keyword('int')
KW_STEP = make_keyword('step')

KW_DO = make_keyword('do')
KW_MOD = make_keyword('mod')
KW_T = make_keyword('T')

# ---------- NonTerminals ----------

NProgram, NFunctionDefs, NFunctionDef, NFunctionHeader, NReturnTypeOpt = \
    map(pe.NonTerminal, 'Program FunctionDefs FunctionDef FunctionHeader ReturnTypeOpt'.split())

NFormalParamsOpt, NFormalParams, NFormalParam, NType, NPrimitiveType = \
    map(pe.NonTerminal, 'FormalParamsOpt FormalParams FormalParam Type PrimitiveType'.split())

NStatementBlock, NStatements, NStatement = \
    map(pe.NonTerminal, 'StatementBlock Statements Statement'.split())

NDeclStatement, NDeclItems, NDeclItem = \
    map(pe.NonTerminal, 'DeclStatement DeclItems DeclItem'.split())

NAssignStatement, NCallStatement, NIfStatement = \
    map(pe.NonTerminal, 'AssignStatement CallStatement IfStatement'.split())

NElsifParts, NElsePartOpt, NWhileStatement = \
    map(pe.NonTerminal, 'ElsifParts ElsePartOpt WhileStatement'.split())

NForStatement, NForInit, NStepOpt, NDoWhileStatement = \
    map(pe.NonTerminal, 'ForStatement ForInit StepOpt DoWhileStatement'.split())

NReturnStatement, NAssertStatement, NExpr, NOrExpr, NOrOp = \
    map(pe.NonTerminal, 'ReturnStatement AssertStatement Expr OrExpr OrOp'.split())

NAndExpr, NCmpExpr, NCmpOp, NAddExpr, NAddOp = \
    map(pe.NonTerminal, 'AndExpr CmpExpr CmpOp AddExpr AddOp'.split())

NMulExpr, NMulOp, NPowExpr, NUnaryExpr, NPostfixExpr = \
    map(pe.NonTerminal, 'MulExpr MulOp PowExpr UnaryExpr PostfixExpr'.split())

NPrimaryExpr, NFunctionCall, NActualParamsOpt, NActualParams, NConstant = \
    map(pe.NonTerminal, 'PrimaryExpr FunctionCall ActualParamsOpt ActualParams Constant'.split())

# ---------- Грамматика ----------

NProgram |= NFunctionDefs, Program

NFunctionDefs |= NFunctionDef, lambda fd: [fd]
NFunctionDefs |= NFunctionDefs, NFunctionDef, lambda fds, fd: fds + [fd]

NFunctionDef |= KW_DEFINE, NFunctionHeader, NStatementBlock, KW_END, \
    lambda header, body: FunctionDef(header[1], header[2], header[0], body)

NFunctionHeader |= NReturnTypeOpt, FUNCNAME, '(', NFormalParamsOpt, ')', \
    lambda rt, name, params: (
        None if isinstance(rt, NoReturnType) else rt,
        name,
        params
    )

NReturnTypeOpt |= NoReturnType
NReturnTypeOpt |= NType

NFormalParamsOpt |= lambda: []
NFormalParamsOpt |= NFormalParams

NFormalParams |= NFormalParam, lambda p: [p]
NFormalParams |= NFormalParams, ',', NFormalParam, lambda ps, p: ps + [p]

NFormalParam |= NType, IDENT, lambda tp, name: Parameter(name, tp)

NType |= NPrimitiveType
NType |= NType, KW_ARRAY, ArrayType

NPrimitiveType |= KW_INT, lambda: Type.Int
NPrimitiveType |= KW_CHAR, lambda: Type.Char
NPrimitiveType |= KW_BOOL, lambda: Type.Bool

NStatementBlock |= lambda: []
NStatementBlock |= NStatements

NStatements |= NStatement, lambda st: [st]
NStatements |= NStatements, ';', NStatement, lambda sts, st: sts + [st]

NStatement |= NDeclStatement
NStatement |= NAssignStatement
NStatement |= NCallStatement
NStatement |= NIfStatement
NStatement |= NWhileStatement
NStatement |= NForStatement
NStatement |= NDoWhileStatement
NStatement |= NReturnStatement
NStatement |= NAssertStatement

NDeclStatement |= NType, NDeclItems, DeclStatement

NDeclItems |= NDeclItem, lambda item: [item]
NDeclItems |= NDeclItems, ',', NDeclItem, lambda items, item: items + [item]

NDeclItem |= IDENT, lambda name: DeclItem(name, None)
NDeclItem |= IDENT, ':=', NExpr, DeclItem

NAssignStatement |= NExpr, ':=', NExpr, AssignStatement

NCallStatement |= NFunctionCall, CallStatement

NIfStatement |= KW_IF, NExpr, KW_THEN, NStatementBlock, NElsifParts, NElsePartOpt, KW_END, \
    lambda cond, then_body, elsifs, else_body: \
        IfStatement([IfBranch(cond, then_body)] + elsifs, else_body)

NElsifParts |= lambda: []
NElsifParts |= NElsifParts, KW_ELSIF, NExpr, KW_THEN, NStatementBlock, \
    lambda branches, cond, body: branches + [IfBranch(cond, body)]

NElsePartOpt |= lambda: []
NElsePartOpt |= KW_ELSE, NStatementBlock, lambda body: body

NWhileStatement |= KW_WHILE, NExpr, KW_DO, NStatementBlock, KW_END, WhileStatement

NForStatement |= NForInit, KW_TO, NExpr, NStepOpt, KW_DO, NStatementBlock, KW_END, \
    lambda init, end, step, body: ForStatement(init[0], init[1], init[2], end, step, body)

NForInit |= IDENT, ':=', NExpr, lambda name, expr: (None, name, expr)
NForInit |= NType, IDENT, ':=', NExpr, lambda tp, name, expr: (tp, name, expr)

NStepOpt |= lambda: ConstExpr('1', Type.Int)
NStepOpt |= KW_STEP, NExpr, lambda expr: expr

NDoWhileStatement |= KW_DO, NStatementBlock, KW_WHILE, NExpr, DoWhileStatement

NReturnStatement |= KW_RETURN, lambda: ReturnStatement(None)
NReturnStatement |= KW_RETURN, NExpr, ReturnStatement

NAssertStatement |= KW_ASSERT, NExpr, AssertStatement

NExpr |= NOrExpr

NOrExpr |= NAndExpr
NOrExpr |= NOrExpr, NOrOp, NAndExpr, BinOpExpr

NOrOp |= KW_OR, lambda: 'or'
NOrOp |= KW_XOR, lambda: 'xor'

NAndExpr |= NCmpExpr
NAndExpr |= NAndExpr, KW_AND, NCmpExpr, lambda left, right: BinOpExpr(left, 'and', right)

NCmpExpr |= NAddExpr
NCmpExpr |= NAddExpr, NCmpOp, NAddExpr, BinOpExpr

NCmpOp |= '=', lambda: '='
NCmpOp |= '<>', lambda: '<>'
NCmpOp |= '<', lambda: '<'
NCmpOp |= '>', lambda: '>'
NCmpOp |= '<=', lambda: '<='
NCmpOp |= '>=', lambda: '>='

NAddExpr |= NMulExpr
NAddExpr |= NAddExpr, NAddOp, NMulExpr, BinOpExpr

NAddOp |= '+', lambda: '+'
NAddOp |= '-', lambda: '-'

NMulExpr |= NPowExpr
NMulExpr |= NMulExpr, NMulOp, NPowExpr, BinOpExpr

NMulOp |= '*', lambda: '*'
NMulOp |= '/', lambda: '/'
NMulOp |= KW_MOD, lambda: 'mod'

NPowExpr |= NUnaryExpr
NPowExpr |= NUnaryExpr, '**', NPowExpr, lambda left, right: BinOpExpr(left, '**', right)

NUnaryExpr |= NPostfixExpr
NUnaryExpr |= '-', NUnaryExpr, lambda expr: UnOpExpr('-', expr)
NUnaryExpr |= KW_NOT, NUnaryExpr, lambda expr: UnOpExpr('not', expr)

NPostfixExpr |= NPrimaryExpr
NPostfixExpr |= NPostfixExpr, '[', NExpr, ']', IndexExpr

NPrimaryExpr |= IDENT, VariableExpr
NPrimaryExpr |= NConstant
NPrimaryExpr |= NFunctionCall
NPrimaryExpr |= KW_NEW, NType, '[', NExpr, ']', NewExpr
NPrimaryExpr |= '(', NExpr, ')'

NFunctionCall |= FUNCNAME, '(', NActualParamsOpt, ')', CallExpr

NActualParamsOpt |= lambda: []
NActualParamsOpt |= NActualParams

NActualParams |= NExpr, lambda expr: [expr]
NActualParams |= NActualParams, ',', NExpr, lambda args, expr: args + [expr]

NConstant |= INT_CONST, lambda value: ConstExpr(value, Type.Int)
NConstant |= CHAR_CONST, lambda value: ConstExpr(value, Type.Char)
NConstant |= STRING_CONST, lambda value: ConstExpr(value, ArrayType(Type.Char))
NConstant |= KW_T, lambda: ConstExpr(True, Type.Bool)
NConstant |= KW_F, lambda: ConstExpr(False, Type.Bool)
NConstant |= KW_NULL, lambda: ConstExpr(None, None)

# ---------- Parser ----------

p = pe.Parser(NProgram, method=pe.EARLEY)

p.add_skipped_domain('\\s')
p.add_skipped_domain('^\\*.*')
p.add_skipped_domain('\\*\\*\\*.*')

# ---------- Main ----------

for filename in sys.argv[1:]:
    try:
        with open(filename) as f:
            tree = p.parse(f.read())
            pprint(tree)
    except pe.Error as e:
        print(f'Ошибка {e.pos}: {e.message}')
    except Exception as e:
        print(e)