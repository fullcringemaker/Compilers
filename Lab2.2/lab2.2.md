% Лабораторная работа № 2.2 «Абстрактные синтаксические деревья»
% 13 апреля 2026 г.
% Дмитрий Трофименко, ИУ9-62Б

# Цель работы
Целью данной работы является получение навыков составления грамматик и проектирования синтаксических деревьев.

# Индивидуальный вариант
Язык [L1](https://hw.iu9.bmstu.ru/static/assets/L1.pdf)

## Синтаксическое расширение для защиты
Добавим синтаксический сахар - разрешим несколько индексов через запятую: 
```text
c := args[0, 1, 2];
```

# Реализация

## Абстрактный синтаксис
Программа в языке L1 представляет собой последовательность определений функций:

```text
Program → Function*
```

Определение функции состоит из имени функции, списка формальных параметров, необязательного типа возвращаемого значения и тела:

```text
Function → FuncName Parameters ReturnType? Statements
```

Формальные параметры — это ноль или более параметров:

```text
Parameters → Parameter*
```

Параметр состоит из имени и типа:

```text
Parameter → VarName Type
```

Тип может быть примитивным или массивным:

```text
Type → int | char | bool | ArrayType
ArrayType → Type
```

Последовательность операторов — это ноль или более операторов:

```text
Statements → Statement*
```

Оператором языка является объявление, присваивание, вызов функции, выбор, цикл с предусловием, цикл `for`, цикл с постусловием, завершение функции или предупреждение:

```text
Statement → DeclStatement
          | AssignStatement
          | CallStatement
          | IfStatement
          | WhileStatement
          | ForStatement
          | DoWhileStatement
          | ReturnStatement
          | AssertStatement
```

### Операторы

Оператор объявления задаёт тип и список объявляемых переменных, каждая из которых может иметь инициализацию:

```text
DeclStatement → Type DeclItem+
DeclItem → VarName Expr?
```

Оператор присваивания связывает изменяемую ячейку с новым значением:

```text
AssignStatement → VariableExpr Expr | ArrayAccessExpr Expr
```

Оператор вызова функции как отдельный оператор:

```text
CallStatement → FuncCallExpr
```

Оператор выбора содержит одну или более условных ветвей и необязательную ветвь `else`:

```text
IfStatement → Branch+ ElseBranch?
Branch → Expr Statements
ElseBranch → Statements
```

Цикл `while` содержит условие и тело:

```text
WhileStatement → Expr Statements
```

Цикл `for` содержит переменную цикла, начальное значение, конечное значение, необязательный шаг и тело:

```text
ForStatement → ForTarget Expr Expr Expr? Statements
ForTarget → VarName | TypedVar
TypedVar → VarName Type
```

Цикл с постусловием состоит из тела и условия:

```text
DoWhileStatement → Statements Expr
```

Оператор завершения функции содержит необязательное возвращаемое выражение:

```text
ReturnStatement → Expr?
```

Оператор-предупреждение содержит проверяемое условие:

```text
AssertStatement → Expr
```

### Выражения

Выражение может быть переменной, константой, вызовом функции, обращением к элементу массива, выделением массива, унарной или бинарной операцией:

```text
Expr → VariableExpr
     | ConstExpr
     | FuncCallExpr
     | ArrayAccessExpr
     | NewArrayExpr
     | UnOpExpr
     | BinOpExpr
```

Переменная определяется именем:

```text
VariableExpr → VarName
```

Константа может быть целочисленной, символьной, строковой, булевой или ссылочной `NULL`:

```text
ConstExpr → IntConst
          | CharConst
          | StringConst
          | BoolConst
          | NullConst
```

Вызов функции состоит из имени и списка фактических параметров:

```text
FuncCallExpr → FuncName Arguments
Arguments → Expr*
```

Доступ к элементу массива состоит из выражения-массива и выражения-индекса:

```text
ArrayAccessExpr → Expr Expr
```

Выделение памяти под массив состоит из типа элементов и выражения размера:

```text
NewArrayExpr → Type Expr
```

Унарная операция:

```text
UnOpExpr → UnOp Expr
UnOp → - | not
```

Бинарная операция:

```text
BinOpExpr → Expr BinOp Expr
BinOp → **
      | * | / | mod
      | + | -
      | = | <> | < | > | <= | >=
      | and | or | xor
```

## Лексическая структура и конкретный синтаксис

### Конкретный синтаксис
```text
Program → FunctionDefs
FunctionDefs → FunctionDef | FunctionDefs FunctionDef

FunctionDef → DEFINE FunctionHeader StatementBlock END
FunctionHeader → ReturnTypeOpt FUNCNAME ( FormalParamsOpt )
ReturnTypeOpt → ε | Type

FormalParamsOpt → ε | FormalParams
FormalParams → FormalParam | FormalParams , FormalParam
FormalParam → Type IDENT

Type → PrimitiveType | Type ARRAY
PrimitiveType → INT | CHAR | BOOL

StatementBlock → ε | Statements
Statements → Statement | Statements ; Statement

Statement → DeclStatement
          | AssignStatement
          | CallStatement
          | IfStatement
          | WhileStatement
          | ForStatement
          | DoWhileStatement
          | ReturnStatement
          | AssertStatement

DeclStatement → Type DeclItems
DeclItems → DeclItem | DeclItems , DeclItem
DeclItem → IDENT | IDENT := Expr

AssignStatement → Expr := Expr
CallStatement → FunctionCall

IfStatement → IF Expr THEN StatementBlock ElsifParts ElsePartOpt END
ElsifParts → ε | ElsifParts ELSIF Expr THEN StatementBlock
ElsePartOpt → ε | ELSE StatementBlock

WhileStatement → WHILE Expr DO StatementBlock END

ForStatement → ForInit TO Expr StepOpt DO StatementBlock END
ForInit → IDENT := Expr | Type IDENT := Expr
StepOpt → ε | STEP Expr

DoWhileStatement → DO StatementBlock WHILE Expr

ReturnStatement → RETURN | RETURN Expr
AssertStatement → ASSERT Expr

Expr → OrExpr

OrExpr → AndExpr | OrExpr OrOp AndExpr
OrOp → OR | XOR

AndExpr → CmpExpr | AndExpr AND CmpExpr

CmpExpr → AddExpr | AddExpr CmpOp AddExpr
CmpOp → = | <> | < | > | <= | >=

AddExpr → MulExpr | AddExpr AddOp MulExpr
AddOp → + | -

MulExpr → PowExpr | MulExpr MulOp PowExpr
MulOp → * | / | MOD

PowExpr → UnaryExpr | UnaryExpr ** PowExpr

UnaryExpr → PostfixExpr | - UnaryExpr | NOT UnaryExpr

PostfixExpr → PrimaryExpr | PostfixExpr [ Expr ]

PrimaryExpr → IDENT
            | Constant
            | FunctionCall
            | NEW Type [ Expr ]
            | ( Expr )

FunctionCall → FUNCNAME ( ActualParamsOpt )

ActualParamsOpt → ε | ActualParams
ActualParams → Expr | ActualParams , Expr

Constant → INT_CONST
         | CHAR_CONST
         | STRING_CONST
         | T
         | F
         | NULL
```

### Лексическая структура:
```text
IDENT = [A-Za-z][A-Za-z0-9_]*
FUNCNAME = [A-Z][A-Za-z0-9_]*(?=\s*\()
INT_CONST = (\{[0-9]+\}[0-9A-Za-z]+|[0-9]+)
CHAR_CONST = '([^'\n]|'')'|\#[A-Z]+|\#\{[0-9A-Fa-f]+\}
STRING_CONST = ("([^"\n])*"|\$QUOT|\$[A-Z]+|\$\{[0-9A-Fa-f]+\})([ \t\r\n]+("([^"\n])*"|\$QUOT|\$[A-Z]+|\$\{[0-9A-Fa-f]+\}))*
```

## Программная реализация

```python
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

# Добавим синтаксический сахар - разрешим несколько индексов через запятую:
def desugar_indices(array, first_index, rest_indices):
    result = IndexExpr(array, first_index)
    for index in rest_indices:
        result = IndexExpr(result, index)
    return result
NPostfixExpr |= NPostfixExpr, '[', NExpr, ',', NActualParams, ']', desugar_indices

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
```

# Тестирование

## Входные данные

```text
define int Abs(int x)
if x < 0 then
    return -x
elsif x = 0 then
    return 0
else
    assert x > 0;
    return x
end
end

define int Main(char array array args)
int a := 5, b := 2, c;
c := Abs(a ** b - 20 / 2 mod 3);
char c := args[0][1][2];
*** Добавим синтаксический сахар - разрешим несколько индексов через запятую:
c := args[0, 1, 2];
return c
end
```

## Вывод на `stdout`

<!-- ENABLE LONG LINES -->

```shell
Program(functions=[FunctionDef(name='Abs',
                               params=[Parameter(name='x',
                                                 type=<Type.Int: 'int'>)],
                               return_type=<Type.Int: 'int'>,
                               body=[IfStatement(branches=[IfBranch(condition=BinOpExpr(left=VariableExpr(varname='x'),
                                                                                        op='<',
                                                                                        right=ConstExpr(value='0',
                                                                                                        type=<Type.Int: 'int'>)),
                                                                    body=[ReturnStatement(expr=UnOpExpr(op='-',
                                                                                                        expr=VariableExpr(varname='x')))]),
                                                           IfBranch(condition=BinOpExpr(left=VariableExpr(varname='x'),
                                                                                        op='=',
                                                                                        right=ConstExpr(value='0',
                                                                                                        type=<Type.Int: 'int'>)),
                                                                    body=[ReturnStatement(expr=ConstExpr(value='0',
                                                                                                         type=<Type.Int: 'int'>))])],
                                                 else_body=[AssertStatement(condition=BinOpExpr(left=VariableExpr(varname='x'),
                                                                                                op='>',
                                                                                                right=ConstExpr(value='0',
                                                                                                                type=<Type.Int: 'int'>))),
                                                            ReturnStatement(expr=VariableExpr(varname='x'))])]),
                   FunctionDef(name='Main',
                               params=[Parameter(name='args',
                                                 type=ArrayType(type=ArrayType(type=<Type.Char: 'char'>)))],
                               return_type=<Type.Int: 'int'>,
                               body=[DeclStatement(type=<Type.Int: 'int'>,
                                                   items=[DeclItem(name='a',
                                                                   expr=ConstExpr(value='5',
                                                                                  type=<Type.Int: 'int'>)),
                                                          DeclItem(name='b',
                                                                   expr=ConstExpr(value='2',
                                                                                  type=<Type.Int: 'int'>)),
                                                          DeclItem(name='c',
                                                                   expr=None)]),
                                     AssignStatement(variable=VariableExpr(varname='c'),
                                                     expr=CallExpr(func='Abs',
                                                                   args=[BinOpExpr(left=BinOpExpr(left=VariableExpr(varname='a'),
                                                                                                  op='**',
                                                                                                  right=VariableExpr(varname='b')),
                                                                                   op='-',
                                                                                   right=BinOpExpr(left=BinOpExpr(left=ConstExpr(value='20',
                                                                                                                                 type=<Type.Int: 'int'>),
                                                                                                                  op='/',
                                                                                                                  right=ConstExpr(value='2',
                                                                                                                                  type=<Type.Int: 'int'>)),
                                                                                                   op='mod',
                                                                                                   right=ConstExpr(value='3',
                                                                                                                   type=<Type.Int: 'int'>)))])),
                                     DeclStatement(type=<Type.Char: 'char'>,
                                                   items=[DeclItem(name='c',
                                                                   expr=IndexExpr(array=IndexExpr(array=IndexExpr(array=VariableExpr(varname='args'),
                                                                                                                  index=ConstExpr(value='0',
                                                                                                                                  type=<Type.Int: 'int'>)),
                                                                                                  index=ConstExpr(value='1',
                                                                                                                  type=<Type.Int: 'int'>)),
                                                                                  index=ConstExpr(value='2',
                                                                                                  type=<Type.Int: 'int'>)))]),
                                     AssignStatement(variable=VariableExpr(varname='c'),
                                                     expr=IndexExpr(array=IndexExpr(array=IndexExpr(array=VariableExpr(varname='args'),
                                                                                                    index=ConstExpr(value='0',
                                                                                                                    type=<Type.Int: 'int'>)),
                                                                                    index=ConstExpr(value='1',
                                                                                                    type=<Type.Int: 'int'>)),
                                                                    index=ConstExpr(value='2',
                                                                                    type=<Type.Int: 'int'>))),
                                     ReturnStatement(expr=VariableExpr(varname='c'))])])
```

# Вывод
В данной лабораторной работе была выполнена разработка описания языка в виде грамматики и построение абстрактного синтаксического дерева, по которому можно однозначно восстановить структуру программы. В рамках задания требовалось определить, какие сущности являются ключевыми для представления программы, как они связаны между собой, и как по входному тексту получать дерево, пригодное для дальнейших этапов компиляции и для вывода в удобном для проверки виде.

В ходе выполнения работы были последовательно разработаны абстрактный синтаксис и конкретный синтаксис, а также лексическая структура, задающая правила распознавания идентификаторов, имён функций и литералов. Далее было спроектировано представление дерева в памяти через набор структур данных, отражающих определения функций, операторы и выражения, включая управление потоком выполнения и работу с массивами. Такое проектирование позволило однозначно сопоставить каждой конструкции входного языка её структурное представление и обеспечить корректное построение дерева при разборе.

На завершающем этапе входной язык был описан средствами библиотеки синтаксического анализа, после чего проведено тестирование на программе, содержащей все заявленные конструкции. Дополнительно было реализовано синтаксическое расширение, позволяющее записывать несколько индексов через запятую, при этом такая запись преобразуется в эквивалентную базовую форму доступа к массиву. Полученный результат подтверждает, что грамматика покрывает требуемые элементы языка, дерево строится корректно, а добавленный синтаксический сахар интегрируется без изменения семантики программы.
