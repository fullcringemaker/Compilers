from __future__ import annotations

import abc
import enum
import typing
from dataclasses import dataclass
from pprint import pprint
import sys

import parser_edsl as pe


MAX_INT = 2147483647

CONTROL_CODES = {
    'NUL': 0,
    'SOH': 1,
    'STX': 2,
    'ETX': 3,
    'EOT': 4,
    'ENQ': 5,
    'ACK': 6,
    'BEL': 7,
    'BS': 8,
    'TAB': 9,
    'LF': 10,
    'VT': 11,
    'FF': 12,
    'CR': 13,
    'SO': 14,
    'SI': 15,
    'DLE': 16,
    'DC1': 17,
    'DC2': 18,
    'DC3': 19,
    'DC4': 20,
    'NAK': 21,
    'SYN': 22,
    'ETB': 23,
    'CAN': 24,
    'EM': 25,
    'SUB': 26,
    'ESC': 27,
    'FS': 28,
    'GS': 29,
    'RS': 30,
    'US': 31,
}


class Type(abc.ABC):
    pass


# PrimitiveType → int | char | bool
class BasicType(enum.Enum):
    Int = 'int'
    Char = 'char'
    Bool = 'bool'


# Type → PrimitiveType
@dataclass
class PrimitiveType(Type):
    kind: BasicType


# Type → Type array
@dataclass
class ArrayType(Type):
    element_type: Type


# Parameter → Type VarName
@dataclass
class Parameter:
    type: Type
    name: str


class Statement(abc.ABC):
    pass


# Program → Function*
@dataclass
class Program:
    functions: list[FunctionDef]


# Function → FuncName Parameters ReturnType? Statements
@dataclass
class FunctionDef:
    name: str
    params: list[Parameter]
    return_type: typing.Optional[Type]
    body: list[Statement]


# DeclItem → VarName Expr?
@dataclass
class DeclItem:
    name: str
    initializer: typing.Optional[Expr]


# Statement → DeclStatement
@dataclass
class DeclarationStatement(Statement):
    type: Type
    items: list[DeclItem]


# Statement → AssignStatement
@dataclass
class AssignStatement(Statement):
    left: Expr
    right: Expr


# Statement → CallStatement
@dataclass
class CallStatement(Statement):
    call: FunctionCallExpr


# Branch → Expr Statements
@dataclass
class IfBranch:
    condition: Expr
    body: list[Statement]


# Statement → IfStatement
@dataclass
class IfStatement(Statement):
    branches: list[IfBranch]
    else_branch: typing.Optional[list[Statement]]


# Statement → WhileStatement
@dataclass
class WhileStatement(Statement):
    condition: Expr
    body: list[Statement]


# ForInit → VarName Expr | VarName Type Expr
@dataclass
class ForInit:
    var_type: typing.Optional[Type]
    name: str
    start: Expr


# Statement → ForStatement
@dataclass
class ForStatement(Statement):
    init: ForInit
    end: Expr
    step: typing.Optional[Expr]
    body: list[Statement]


# Statement → DoWhileStatement
@dataclass
class DoWhileStatement(Statement):
    body: list[Statement]
    condition: Expr


# Statement → ReturnStatement
@dataclass
class ReturnStatement(Statement):
    expr: typing.Optional[Expr]


# Statement → AssertStatement
@dataclass
class AssertStatement(Statement):
    condition: Expr


class Expr(abc.ABC):
    pass


# Expr → VarName
@dataclass
class VariableExpr(Expr):
    name: str


# Expr → Const
# Const → IntConst | CharConst | StringConst | BoolConst | NullConst
@dataclass
class ConstExpr(Expr):
    value: typing.Any
    kind: str


# Expr → FuncCallExpr
@dataclass
class FunctionCallExpr(Expr):
    name: str
    args: list[Expr]


# Expr → Expr Expr
@dataclass
class ArrayAccessExpr(Expr):
    array: Expr
    index: Expr


# Expr → Type Expr
@dataclass
class NewArrayExpr(Expr):
    type: Type
    size: Expr


# Expr → UnOp Expr
@dataclass
class UnOpExpr(Expr):
    op: str
    expr: Expr


# Expr → Expr BinOp Expr
@dataclass
class BinOpExpr(Expr):
    left: Expr
    op: str
    right: Expr


def parse_int_literal(image: str) -> int:
    if image.startswith('{'):
        closing = image.find('}')
        if closing == -1:
            raise pe.TokenAttributeError(f'Некорректная целочисленная константа: {image}')

        base = int(image[1:closing])
        digits = image[closing + 1:]
        if not (2 <= base <= 36):
            raise pe.TokenAttributeError(f'Недопустимое основание системы счисления: {base}')
        if not digits:
            raise pe.TokenAttributeError(f'Некорректная целочисленная константа: {image}')

        try:
            value = int(digits, base)
        except ValueError:
            raise pe.TokenAttributeError(f'Некорректная запись числа: {image}')
    else:
        value = int(image, 10)

    if value > MAX_INT:
        raise pe.TokenAttributeError(f'Слишком большое целое число: {image}')

    return value


def parse_char_literal(image: str) -> str:
    if image.startswith("'"):
        inner = image[1:-1].replace("''", "'")
        if len(inner) != 1:
            raise pe.TokenAttributeError(f'Символьная константа должна содержать ровно один символ: {image}')
        return inner

    if image.startswith('#{') and image.endswith('}'):
        code = int(image[2:-1], 16)
        return chr(code)

    if image.startswith('#'):
        name = image[1:]
        if name not in CONTROL_CODES:
            raise pe.TokenAttributeError(f'Неизвестная аббревиатура управляющего символа: {image}')
        return chr(CONTROL_CODES[name])

    raise pe.TokenAttributeError(f'Некорректная символьная константа: {image}')


def parse_string_text_section(image: str) -> str:
    return image[1:-1]


def parse_string_control_section(image: str) -> str:
    if image == '$QUOT':
        return '"'

    if image.startswith('${') and image.endswith('}'):
        code = int(image[2:-1], 16)
        return chr(code)

    name = image[1:]
    if name not in CONTROL_CODES:
        raise pe.TokenAttributeError(f'Неизвестная строковая секция: {image}')
    return chr(CONTROL_CODES[name])


IDENT = pe.Terminal('IDENT', r'[^\W\d_]\w*', str)
INT_CONST = pe.Terminal(
    'INT_CONST',
    r'(?:\{\d+\}[0-9A-Za-z]+|[0-9]+)',
    parse_int_literal,
    priority=7,
)
CHAR_CONST = pe.Terminal(
    'CHAR_CONST',
    r"(?:'(?:[^'\n]|'')+'|\#[A-Za-z][A-Za-z0-9]*|\#\{[0-9A-Fa-f]+\})",
    parse_char_literal,
    priority=7,
)
STRING_TEXT_SECTION = pe.Terminal(
    'STRING_TEXT_SECTION',
    r'"[^"\x00-\x1F]*"',
    parse_string_text_section,
    priority=7,
)
STRING_CONTROL_SECTION = pe.Terminal(
    'STRING_CONTROL_SECTION',
    r'\$(?:[A-Z][A-Z0-9]*|\{[0-9A-Fa-f]+\})',
    parse_string_control_section,
    priority=7,
)


(NProgram, NFunctionDefs, NFunctionDef, NReturnTypeOpt, NFormalParamsOpt,
 NFormalParams, NFormalParam, NType, NPrimitiveType, NStatementBlock,
 NStatements, NStatement, NDeclStatement, NDeclItems, NDeclItem,
 NAssignStatement, NCallStatement, NIfStatement, NElsifParts,
 NElsePartOpt, NWhileStatement, NForStatement, NForInit, NStepOpt,
 NDoWhileStatement, NReturnStatement, NAssertStatement, NExpr,
 NOrExpr, NOrOp, NAndExpr, NCmpExpr, NCmpOp, NAddExpr, NAddOp,
 NMulExpr, NMulOp, NPowExpr, NUnaryExpr, NPostfixExpr, NPrimaryExpr,
 NFunctionCall, NActualParamsOpt, NActualParams, NConst,
 NStringConst, NStringSection) = map(
    pe.NonTerminal,
    'Program FunctionDefs FunctionDef ReturnTypeOpt FormalParamsOpt '
    'FormalParams FormalParam Type PrimitiveType StatementBlock '
    'Statements Statement DeclStatement DeclItems DeclItem '
    'AssignStatement CallStatement IfStatement ElsifParts '
    'ElsePartOpt WhileStatement ForStatement ForInit StepOpt '
    'DoWhileStatement ReturnStatement AssertStatement Expr '
    'OrExpr OrOp AndExpr CmpExpr CmpOp AddExpr AddOp '
    'MulExpr MulOp PowExpr UnaryExpr PostfixExpr PrimaryExpr '
    'FunctionCall ActualParamsOpt ActualParams Const '
    'StringConst StringSection'.split()
)

NProgram |= NFunctionDefs, Program

NFunctionDefs |= NFunctionDef, lambda fd: [fd]
NFunctionDefs |= NFunctionDefs, NFunctionDef, lambda fds, fd: fds + [fd]

NFunctionDef |= (
    'define', NReturnTypeOpt, IDENT, '(', NFormalParamsOpt, ')',
    NStatementBlock, 'end',
    lambda return_type, name, params, body: FunctionDef(name, params, return_type, body)
)

NReturnTypeOpt |= lambda: None
NReturnTypeOpt |= NType

NFormalParamsOpt |= lambda: []
NFormalParamsOpt |= NFormalParams

NFormalParams |= NFormalParam, lambda p: [p]
NFormalParams |= NFormalParams, ',', NFormalParam, lambda ps, p: ps + [p]

NFormalParam |= NType, IDENT, Parameter

NType |= NPrimitiveType
NType |= NType, 'array', ArrayType

NPrimitiveType |= 'int', lambda: PrimitiveType(BasicType.Int)
NPrimitiveType |= 'char', lambda: PrimitiveType(BasicType.Char)
NPrimitiveType |= 'bool', lambda: PrimitiveType(BasicType.Bool)

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

NDeclStatement |= NType, NDeclItems, DeclarationStatement

NDeclItems |= NDeclItem, lambda item: [item]
NDeclItems |= NDeclItems, ',', NDeclItem, lambda items, item: items + [item]

NDeclItem |= IDENT, lambda name: DeclItem(name, None)
NDeclItem |= IDENT, ':=', NExpr, DeclItem

NAssignStatement |= NExpr, ':=', NExpr, AssignStatement

NCallStatement |= NFunctionCall, CallStatement

NIfStatement |= (
    'if', NExpr, 'then', NStatementBlock, NElsifParts, NElsePartOpt, 'end',
    lambda cond, then_body, elsifs, else_body:
        IfStatement([IfBranch(cond, then_body)] + elsifs, else_body)
)

NElsifParts |= lambda: []
NElsifParts |= (
    NElsifParts, 'elsif', NExpr, 'then', NStatementBlock,
    lambda parts, cond, body: parts + [IfBranch(cond, body)]
)

NElsePartOpt |= lambda: None
NElsePartOpt |= 'else', NStatementBlock, lambda body: body

NWhileStatement |= 'while', NExpr, 'do', NStatementBlock, 'end', WhileStatement

NForInit |= IDENT, ':=', NExpr, lambda name, start: ForInit(None, name, start)
NForInit |= NType, IDENT, ':=', NExpr, lambda var_type, name, start: ForInit(var_type, name, start)

NStepOpt |= lambda: None
NStepOpt |= 'step', NExpr, lambda expr: expr

NForStatement |= (
    NForInit, 'to', NExpr, NStepOpt, 'do', NStatementBlock, 'end',
    lambda init, end_expr, step, body: ForStatement(init, end_expr, step, body)
)

NDoWhileStatement |= 'do', NStatementBlock, 'while', NExpr, lambda body, cond: DoWhileStatement(body, cond)

NReturnStatement |= 'return', lambda: ReturnStatement(None)
NReturnStatement |= 'return', NExpr, ReturnStatement

NAssertStatement |= 'assert', NExpr, AssertStatement

NExpr |= NOrExpr

NOrExpr |= NAndExpr
NOrExpr |= NOrExpr, NOrOp, NAndExpr, BinOpExpr

NOrOp |= 'or', lambda: 'or'
NOrOp |= 'xor', lambda: 'xor'

NAndExpr |= NCmpExpr
NAndExpr |= NAndExpr, 'and', NCmpExpr, lambda left, right: BinOpExpr(left, 'and', right)

NCmpExpr |= NAddExpr
NCmpExpr |= NAddExpr, NCmpOp, NAddExpr, BinOpExpr

for op in ('=', '<>', '<', '>', '<=', '>='):
    NCmpOp |= op, (lambda value=op: lambda: value)()

NAddExpr |= NMulExpr
NAddExpr |= NAddExpr, NAddOp, NMulExpr, BinOpExpr

NAddOp |= '+', lambda: '+'
NAddOp |= '-', lambda: '-'

NMulExpr |= NPowExpr
NMulExpr |= NMulExpr, NMulOp, NPowExpr, BinOpExpr

NMulOp |= '*', lambda: '*'
NMulOp |= '/', lambda: '/'
NMulOp |= 'mod', lambda: 'mod'

NPowExpr |= NUnaryExpr
NPowExpr |= NUnaryExpr, '**', NPowExpr, lambda left, right: BinOpExpr(left, '**', right)

NUnaryExpr |= NPostfixExpr
NUnaryExpr |= '-', NUnaryExpr, lambda expr: UnOpExpr('-', expr)
NUnaryExpr |= 'not', NUnaryExpr, lambda expr: UnOpExpr('not', expr)

NPostfixExpr |= NPrimaryExpr
NPostfixExpr |= NPostfixExpr, '[', NExpr, ']', ArrayAccessExpr

NPrimaryExpr |= IDENT, VariableExpr
NPrimaryExpr |= NConst
NPrimaryExpr |= NFunctionCall
NPrimaryExpr |= 'new', NType, '[', NExpr, ']', NewArrayExpr
NPrimaryExpr |= '(', NExpr, ')'

NFunctionCall |= IDENT, '(', NActualParamsOpt, ')', FunctionCallExpr

NActualParamsOpt |= lambda: []
NActualParamsOpt |= NActualParams

NActualParams |= NExpr, lambda expr: [expr]
NActualParams |= NActualParams, ',', NExpr, lambda exprs, expr: exprs + [expr]

NConst |= INT_CONST, lambda value: ConstExpr(value, 'int')
NConst |= CHAR_CONST, lambda value: ConstExpr(value, 'char')
NConst |= NStringConst, lambda value: ConstExpr(value, 'string')
NConst |= 'T', lambda: ConstExpr(True, 'bool')
NConst |= 'F', lambda: ConstExpr(False, 'bool')
NConst |= 'NULL', lambda: ConstExpr(None, 'null')

NStringConst |= NStringSection
NStringConst |= NStringConst, NStringSection, lambda value, section: value + section

NStringSection |= STRING_TEXT_SECTION
NStringSection |= STRING_CONTROL_SECTION

parser = pe.Parser(NProgram)

parser.add_skipped_domain(r'\s+')
parser.add_skipped_domain(r'^\*[^\n]*')
parser.add_skipped_domain(r'\*\*\*[^\n]*')


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        try:
            with open(filename, encoding='utf-8') as f:
                tree = parser.parse(f.read())
                pprint(tree)
        except pe.Error as e:
            print(f'Ошибка {e.pos}: {e.message}')
        except Exception as e:
            print(e)

