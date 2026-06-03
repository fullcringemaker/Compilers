import abc
import enum
import typing
from dataclasses import dataclass, field
import parser_edsl as pe
import re
import sys

# ---------- Узлы типов ----------

class Type(enum.Enum):
    Int = 'int'
    Char = 'char'
    Bool = 'bool'

@dataclass(frozen=True)
class ArrayType:
    type: typing.Any

@dataclass
class NoReturnType:
    pass

# ---------- Семантические ошибки ----------

class SemanticError(pe.Error):
    pass

class DuplicateFunction(SemanticError):
    def __init__(self, pos, name):
        self.pos = pos
        self.name = name

    @property
    def message(self):
        return f'Повторное определение функции {self.name}'

class DuplicateVariable(SemanticError):
    def __init__(self, pos, name):
        self.pos = pos
        self.name = name

    @property
    def message(self):
        return f'Повторное объявление переменной {self.name}'

class UnknownFunction(SemanticError):
    def __init__(self, pos, name):
        self.pos = pos
        self.name = name

    @property
    def message(self):
        return f'Необъявленная функция {self.name}'

class UnknownVariable(SemanticError):
    def __init__(self, pos, name):
        self.pos = pos
        self.name = name

    @property
    def message(self):
        return f'Необъявленная переменная {self.name}'

class BadArgumentCount(SemanticError):
    def __init__(self, pos, name, expected, actual):
        self.pos = pos
        self.name = name
        self.expected = expected
        self.actual = actual

    @property
    def message(self):
        return f'Функция {self.name} ожидает {self.expected} аргументов, получено {self.actual}'

class BadArgumentType(SemanticError):
    def __init__(self, pos, name, number, expected, actual):
        self.pos = pos
        self.name = name
        self.number = number
        self.expected = expected
        self.actual = actual

    @property
    def message(self):
        return (
            f'Несовместимый тип {self.number}-го аргумента функции {self.name}: '
            f'ожидалось {type_to_str(self.expected)}, получено {type_to_str(self.actual)}'
        )

class ProcedureUsedAsExpression(SemanticError):
    def __init__(self, pos, name):
        self.pos = pos
        self.name = name

    @property
    def message(self):
        return f'Функция {self.name} не возвращает значение'

class FunctionUsedAsStatement(SemanticError):
    def __init__(self, pos, name):
        self.pos = pos
        self.name = name

    @property
    def message(self):
        return f'Функция {self.name} возвращает значение и не может использоваться как оператор вызова'

class BadBinaryType(SemanticError):
    def __init__(self, pos, left, op, right):
        self.pos = pos
        self.left = left
        self.op = op
        self.right = right

    @property
    def message(self):
        return f'Недопустимые типы операндов: {type_to_str(self.left)} {self.op} {type_to_str(self.right)}'

class BadUnaryType(SemanticError):
    def __init__(self, pos, op, type_):
        self.pos = pos
        self.op = op
        self.type = type_

    @property
    def message(self):
        return f'Недопустимый тип операнда: {self.op} {type_to_str(self.type)}'

class BadAssignmentType(SemanticError):
    def __init__(self, pos, target, source):
        self.pos = pos
        self.target = target
        self.source = source

    @property
    def message(self):
        return f'Несовместимые типы присваивания: {type_to_str(self.target)} := {type_to_str(self.source)}'

class BadConditionType(SemanticError):
    def __init__(self, pos, type_):
        self.pos = pos
        self.type = type_

    @property
    def message(self):
        return f'Условие имеет тип {type_to_str(self.type)} вместо bool'

class NotLValue(SemanticError):
    def __init__(self, pos):
        self.pos = pos

    @property
    def message(self):
        return 'Левая часть присваивания не является изменяемой ячейкой'

class ImmutableVariable(SemanticError):
    def __init__(self, pos, name):
        self.pos = pos
        self.name = name

    @property
    def message(self):
        return f'Переменная {self.name} является неизменяемой'

class BadIndexing(SemanticError):
    def __init__(self, pos, type_):
        self.pos = pos
        self.type = type_

    @property
    def message(self):
        return f'Индексирование применено не к массиву, а к {type_to_str(self.type)}'

class BadIndexType(SemanticError):
    def __init__(self, pos, type_):
        self.pos = pos
        self.type = type_

    @property
    def message(self):
        return f'Индекс массива имеет тип {type_to_str(self.type)} вместо int или char'

class BadNewSizeType(SemanticError):
    def __init__(self, pos, type_):
        self.pos = pos
        self.type = type_

    @property
    def message(self):
        return f'Размер массива имеет тип {type_to_str(self.type)} вместо int'

class BadForVariableType(SemanticError):
    def __init__(self, pos, type_):
        self.pos = pos
        self.type = type_

    @property
    def message(self):
        return f'Переменная цикла имеет тип {type_to_str(self.type)} вместо int или char'

class BadForStepType(SemanticError):
    def __init__(self, pos, type_):
        self.pos = pos
        self.type = type_

    @property
    def message(self):
        return f'Шаг цикла имеет тип {type_to_str(self.type)} вместо int'

class BadReturnType(SemanticError):
    def __init__(self, pos, expected, actual):
        self.pos = pos
        self.expected = expected
        self.actual = actual

    @property
    def message(self):
        return f'Несовместимый тип return: ожидалось {type_to_str(self.expected)}, получено {type_to_str(self.actual)}'

class MissingReturnValue(SemanticError):
    def __init__(self, pos, expected):
        self.pos = pos
        self.expected = expected

    @property
    def message(self):
        return f'Оператор return должен возвращать значение типа {type_to_str(self.expected)}'

class UnexpectedReturnValue(SemanticError):
    def __init__(self, pos, actual):
        self.pos = pos
        self.actual = actual

    @property
    def message(self):
        return f'Процедура не должна возвращать значение типа {type_to_str(self.actual)}'

# ---------- Проверка типов ----------

def type_to_str(type_):
    if type_ is None:
        return 'NULL'
    if isinstance(type_, Type):
        return type_.value
    if isinstance(type_, ArrayType):
        return f'{type_to_str(type_.type)} array'
    return str(type_)

def same_type(left, right):
    return left == right

def is_array_type(type_):
    return isinstance(type_, ArrayType)

def assignment_compatible(target, source):
    if same_type(target, source):
        return True
    if target == Type.Int and source == Type.Char:
        return True
    if is_array_type(target) and source is None:
        return True
    return False

def binary_result_type(left, op, right):
    if op == '+':
        if left == Type.Int and right == Type.Int:
            return Type.Int
        if left == Type.Int and right == Type.Char:
            return Type.Char
        if left == Type.Char and right == Type.Int:
            return Type.Char
        return None

    if op == '-':
        if left == Type.Int and right == Type.Int:
            return Type.Int
        if left == Type.Char and right == Type.Char:
            return Type.Int
        if left == Type.Char and right == Type.Int:
            return Type.Char
        return None

    if op in ('**', '*', '/', 'mod'):
        if left == Type.Int and right == Type.Int:
            return Type.Int
        return None

    if op in ('=', '<>'):
        if (left, right) in (
            (Type.Int, Type.Int),
            (Type.Int, Type.Char),
            (Type.Char, Type.Int),
            (Type.Char, Type.Char),
            (Type.Bool, Type.Bool),
        ):
            return Type.Bool
        if is_array_type(left) and is_array_type(right) and same_type(left, right):
            return Type.Bool
        if is_array_type(left) and right is None:
            return Type.Bool
        if left is None and is_array_type(right):
            return Type.Bool
        return None

    if op in ('<', '>', '<=', '>='):
        if (left, right) in (
            (Type.Int, Type.Int),
            (Type.Int, Type.Char),
            (Type.Char, Type.Int),
            (Type.Char, Type.Char),
        ):
            return Type.Bool
        return None

    if op in ('and', 'or', 'xor'):
        if left == Type.Bool and right == Type.Bool:
            return Type.Bool
        return None

    return None

# ---------- Символы и локальные таблицы символов ----------

@dataclass
class VariableSymbol:
    name: str
    type: typing.Any
    pos: pe.Position
    mutable: bool

@dataclass
class FunctionSymbol:
    name: str
    return_type: typing.Optional[typing.Any]
    params: list
    pos: pe.Position

@dataclass
class SymbolTable:
    symbols: dict = field(default_factory=dict)
    open_scopes: list = field(default_factory=list)

    def add_open_scope(self, table):
        if table is not None:
            self.open_scopes.append(table)

    def contains_symbol(self, name):
        return name in self.symbols

    def add_symbol(self, symbol):
        if self.contains_symbol(symbol.name):
            return False
        self.symbols[symbol.name] = symbol
        return True

    def find_symbol(self, name):
        if name in self.symbols:
            return self.symbols[name]

        for table in self.open_scopes:
            found = table.find_symbol(name)
            if found is not None:
                return found

        return None

@dataclass
class SemanticContext:
    functions: SymbolTable
    scope: SymbolTable
    return_type: typing.Optional[typing.Any]

    @staticmethod
    def is_mutable_name(name):
        return bool(name) and name[0].islower()

    def make_child(self, local_table):
        local_table.add_open_scope(self.scope)
        return SemanticContext(self.functions, local_table, self.return_type)

# ---------- Узлы абстрактного синтаксического дерева ----------

@dataclass
class Parameter:
    name: str
    name_coord: pe.Position
    type: typing.Any

    @pe.ExAction
    def create(attrs, coords, res_coord):
        type_, name = attrs
        ctype, cname = coords
        return Parameter(name, cname.start, type_)

class Statement(abc.ABC):
    @abc.abstractmethod
    def check(self, context):
        pass

class Expr(abc.ABC):
    @abc.abstractmethod
    def check(self, context):
        pass

    def error_pos(self):
        coord = getattr(self, 'coord', None)
        if coord is not None:
            return coord.start
        return pe.Position()

    def check_lvalue(self, context):
        self.check(context)
        raise NotLValue(self.error_pos())

@dataclass
class StatementBlock:
    statements: list
    local_table: typing.Optional[SymbolTable] = field(default=None, init=False)

    def check(self, context):
        self.local_table = SymbolTable()
        block_context = context.make_child(self.local_table)

        for statement in self.statements:
            statement.check(block_context)

@dataclass
class Program:
    functions: list
    local_table: typing.Optional[SymbolTable] = field(default=None, init=False)

    def check(self):
        self.local_table = SymbolTable()

        for function in self.functions:
            if self.local_table.contains_symbol(function.name):
                raise DuplicateFunction(function.name_coord, function.name)

            symbol = FunctionSymbol(
                function.name,
                function.return_type,
                [param.type for param in function.params],
                function.name_coord,
            )
            self.local_table.add_symbol(symbol)

        context = SemanticContext(self.local_table, self.local_table, None)

        for function in self.functions:
            function.check(context)

@dataclass
class FunctionHeader:
    return_type: typing.Optional[typing.Any]
    name: str
    name_coord: pe.Position
    params: list

    @pe.ExAction
    def create(attrs, coords, res_coord):
        return_type, name, params = attrs
        creturn, cname, clparen, cparams, crparen = coords

        if isinstance(return_type, NoReturnType):
            return_type = None

        return FunctionHeader(return_type, name, cname.start, params)

@dataclass
class FunctionDef:
    name: str
    name_coord: pe.Position
    params: list
    return_type: typing.Optional[typing.Any]
    body: StatementBlock
    local_table: typing.Optional[SymbolTable] = field(default=None, init=False)

    def check(self, context):
        self.local_table = SymbolTable()
        function_context = SemanticContext(context.functions, self.local_table, self.return_type)

        for param in self.params:
            symbol = VariableSymbol(
                param.name,
                param.type,
                param.name_coord,
                SemanticContext.is_mutable_name(param.name),
            )

            if not self.local_table.add_symbol(symbol):
                raise DuplicateVariable(param.name_coord, param.name)

        self.body.check(function_context)

@dataclass
class DeclItem:
    name: str
    name_coord: pe.Position
    expr: typing.Optional[Expr]
    assign_coord: typing.Optional[pe.Position] = None

    @pe.ExAction
    def create(attrs, coords, res_coord):
        if len(attrs) == 1:
            name, = attrs
            cname, = coords
            return DeclItem(name, cname.start, None)

        name, expr = attrs
        cname, cassign, cexpr = coords
        return DeclItem(name, cname.start, expr, cassign.start)

@dataclass
class DeclStatement(Statement):
    type: typing.Any
    items: list

    def check(self, context):
        for item in self.items:
            if context.scope.contains_symbol(item.name):
                raise DuplicateVariable(item.name_coord, item.name)

            if item.expr is not None:
                item.expr.check(context)

                if not assignment_compatible(self.type, item.expr.type):
                    raise BadAssignmentType(item.assign_coord, self.type, item.expr.type)

            symbol = VariableSymbol(
                item.name,
                self.type,
                item.name_coord,
                SemanticContext.is_mutable_name(item.name),
            )

            context.scope.add_symbol(symbol)

@dataclass
class AssignStatement(Statement):
    variable: Expr
    expr: Expr
    assign_coord: pe.Position

    @pe.ExAction
    def create(attrs, coords, res_coord):
        variable, expr = attrs
        cvariable, cassign, cexpr = coords
        return AssignStatement(variable, expr, cassign.start)

    def check(self, context):
        target_type = self.variable.check_lvalue(context)
        self.expr.check(context)

        if not assignment_compatible(target_type, self.expr.type):
            raise BadAssignmentType(self.assign_coord, target_type, self.expr.type)

@dataclass
class CallExpr(Expr):
    func: str
    func_coord: pe.Position
    args: list
    coord: pe.Fragment = None
    type: typing.Any = None

    @pe.ExAction
    def create(attrs, coords, res_coord):
        func, args = attrs
        cfunc, clparen, cargs, crparen = coords
        return CallExpr(func, cfunc.start, args, res_coord)

    def check_call(self, context):
        function = context.functions.find_symbol(self.func)

        if function is None or not isinstance(function, FunctionSymbol):
            raise UnknownFunction(self.func_coord, self.func)

        if len(self.args) != len(function.params):
            raise BadArgumentCount(self.func_coord, self.func, len(function.params), len(self.args))

        for number, pair in enumerate(zip(self.args, function.params), start=1):
            arg, expected_type = pair
            arg.check(context)

            if not same_type(expected_type, arg.type):
                raise BadArgumentType(arg.error_pos(), self.func, number, expected_type, arg.type)

        self.type = function.return_type

    def check(self, context):
        self.check_call(context)

        if self.type is None:
            raise ProcedureUsedAsExpression(self.func_coord, self.func)

@dataclass
class CallStatement(Statement):
    call: CallExpr

    def check(self, context):
        self.call.check_call(context)

        if self.call.type is not None:
            raise FunctionUsedAsStatement(self.call.func_coord, self.call.func)

@dataclass
class IfBranch:
    condition: Expr
    condition_coord: pe.Fragment
    body: StatementBlock

    @pe.ExAction
    def create(attrs, coords, res_coord):
        branches, condition, body = attrs
        cbranches, celsif, ccondition, cthen, cbody = coords
        return branches + [IfBranch(condition, ccondition, body)]

@dataclass
class IfStatement(Statement):
    branches: list
    else_body: StatementBlock

    @pe.ExAction
    def create(attrs, coords, res_coord):
        condition, then_body, elsif_parts, else_body = attrs
        cif, ccondition, cthen, cthen_body, celsifs, celse_body, cend = coords
        return IfStatement([IfBranch(condition, ccondition, then_body)] + elsif_parts, else_body)

    def check(self, context):
        for branch in self.branches:
            branch.condition.check(context)

            if branch.condition.type != Type.Bool:
                raise BadConditionType(branch.condition_coord.start, branch.condition.type)

            branch.body.check(context)

        self.else_body.check(context)

@dataclass
class WhileStatement(Statement):
    condition: Expr
    condition_coord: pe.Fragment
    body: StatementBlock

    @pe.ExAction
    def create(attrs, coords, res_coord):
        condition, body = attrs
        cwhile, ccondition, cdo, cbody, cend = coords
        return WhileStatement(condition, ccondition, body)

    def check(self, context):
        self.condition.check(context)

        if self.condition.type != Type.Bool:
            raise BadConditionType(self.condition_coord.start, self.condition.type)

        self.body.check(context)

@dataclass
class ForInit:
    type: typing.Optional[typing.Any]
    variable: str
    variable_coord: pe.Position
    assign_coord: pe.Position
    start: Expr

    @staticmethod
    def create(with_type):
        @pe.ExAction
        def action(attrs, coords, res_coord):
            if with_type:
                type_, variable, start = attrs
                ctype, cvariable, cassign, cstart = coords
                return ForInit(type_, variable, cvariable.start, cassign.start, start)

            variable, start = attrs
            cvariable, cassign, cstart = coords
            return ForInit(None, variable, cvariable.start, cassign.start, start)

        return action

@dataclass
class ForStatement(Statement):
    type: typing.Optional[typing.Any]
    variable: str
    variable_coord: pe.Position
    assign_coord: pe.Position
    start: Expr
    end: Expr
    end_coord: pe.Fragment
    step: Expr
    step_coord: pe.Fragment
    body: StatementBlock
    local_table: typing.Optional[SymbolTable] = field(default=None, init=False)

    @pe.ExAction
    def create(attrs, coords, res_coord):
        init, end, step, body = attrs
        cinit, cto, cend_expr, cstep, cdo, cbody, cend_kw = coords

        return ForStatement(
            init.type,
            init.variable,
            init.variable_coord,
            init.assign_coord,
            init.start,
            end,
            cend_expr,
            step,
            cstep,
            body,
        )

    def check(self, context):
        self.local_table = SymbolTable()
        loop_context = context.make_child(self.local_table)

        self.start.check(context)

        if self.type is None:
            symbol = context.scope.find_symbol(self.variable)

            if symbol is None or not isinstance(symbol, VariableSymbol):
                raise UnknownVariable(self.variable_coord, self.variable)

            variable_type = symbol.type

            if not symbol.mutable:
                raise ImmutableVariable(self.variable_coord, self.variable)
        else:
            symbol = VariableSymbol(
                self.variable,
                self.type,
                self.variable_coord,
                SemanticContext.is_mutable_name(self.variable),
            )

            if not self.local_table.add_symbol(symbol):
                raise DuplicateVariable(self.variable_coord, self.variable)

            if not symbol.mutable:
                raise ImmutableVariable(self.variable_coord, self.variable)

            variable_type = self.type

        if variable_type not in (Type.Int, Type.Char):
            raise BadForVariableType(self.variable_coord, variable_type)

        if not assignment_compatible(variable_type, self.start.type):
            raise BadAssignmentType(self.assign_coord, variable_type, self.start.type)

        self.end.check(loop_context)

        if not assignment_compatible(variable_type, self.end.type):
            raise BadAssignmentType(self.end_coord.start, variable_type, self.end.type)

        self.step.check(loop_context)

        if self.step.type != Type.Int:
            raise BadForStepType(self.step_coord.start, self.step.type)

        self.body.check(loop_context)

@dataclass
class DoWhileStatement(Statement):
    body: StatementBlock
    condition: Expr
    condition_coord: pe.Fragment

    @pe.ExAction
    def create(attrs, coords, res_coord):
        body, condition = attrs
        cdo, cbody, cwhile, ccondition = coords
        return DoWhileStatement(body, condition, ccondition)

    def check(self, context):
        self.body.check(context)
        self.condition.check(context)

        if self.condition.type != Type.Bool:
            raise BadConditionType(self.condition_coord.start, self.condition.type)

@dataclass
class ReturnStatement(Statement):
    expr: typing.Optional[Expr]
    return_coord: pe.Position
    expr_coord: typing.Optional[pe.Fragment] = None

    @pe.ExAction
    def create(attrs, coords, res_coord):
        if len(attrs) == 0:
            creturn, = coords
            return ReturnStatement(None, creturn.start)

        expr, = attrs
        creturn, cexpr = coords
        return ReturnStatement(expr, creturn.start, cexpr)

    def check(self, context):
        if context.return_type is None:
            if self.expr is None:
                return

            self.expr.check(context)
            raise UnexpectedReturnValue(self.return_coord, self.expr.type)

        if self.expr is None:
            raise MissingReturnValue(self.return_coord, context.return_type)

        self.expr.check(context)

        if not same_type(context.return_type, self.expr.type):
            raise BadReturnType(self.expr_coord.start, context.return_type, self.expr.type)

@dataclass
class AssertStatement(Statement):
    condition: Expr
    condition_coord: pe.Fragment

    @pe.ExAction
    def create(attrs, coords, res_coord):
        condition, = attrs
        cassert, ccondition = coords
        return AssertStatement(condition, ccondition)

    def check(self, context):
        self.condition.check(context)

        if self.condition.type != Type.Bool:
            raise BadConditionType(self.condition_coord.start, self.condition.type)

@dataclass
class VariableExpr(Expr):
    varname: str
    var_coord: pe.Position
    coord: pe.Fragment = None
    type: typing.Any = None
    mutable: bool = False

    @pe.ExAction
    def create(attrs, coords, res_coord):
        varname, = attrs
        cvarname, = coords
        return VariableExpr(varname, cvarname.start, res_coord)

    def check(self, context):
        symbol = context.scope.find_symbol(self.varname)

        if symbol is None or not isinstance(symbol, VariableSymbol):
            raise UnknownVariable(self.var_coord, self.varname)

        self.type = symbol.type
        self.mutable = symbol.mutable

    def check_lvalue(self, context):
        self.check(context)

        if not self.mutable:
            raise ImmutableVariable(self.var_coord, self.varname)

        return self.type

@dataclass
class ConstExpr(Expr):
    value: typing.Any
    type: typing.Any
    coord: pe.Fragment = None

    @staticmethod
    def create(type_, value_marker=None):
        @pe.ExAction
        def action(attrs, coords, res_coord):
            if value_marker is None and len(attrs) == 1:
                value, = attrs
            else:
                value = value_marker

            return ConstExpr(value, type_, res_coord)

        return action

    def check(self, context):
        pass

@dataclass
class IndexExpr(Expr):
    array: Expr
    index: Expr
    bracket_coord: pe.Position
    index_coord: pe.Fragment
    coord: pe.Fragment = None
    type: typing.Any = None

    @pe.ExAction
    def create(attrs, coords, res_coord):
        array, index = attrs
        carray, copen, cindex, cclose = coords
        return IndexExpr(array, index, copen.start, cindex, res_coord)

    def check(self, context):
        self.array.check(context)

        if not is_array_type(self.array.type):
            raise BadIndexing(self.bracket_coord, self.array.type)

        self.index.check(context)

        if self.index.type not in (Type.Int, Type.Char):
            raise BadIndexType(self.index_coord.start, self.index.type)

        self.type = self.array.type.type

    def check_lvalue(self, context):
        self.check(context)
        return self.type

@dataclass
class NewExpr(Expr):
    element_type: typing.Any
    size: Expr
    new_coord: pe.Position
    size_coord: pe.Fragment
    coord: pe.Fragment = None
    type: typing.Any = None

    @pe.ExAction
    def create(attrs, coords, res_coord):
        element_type, size = attrs
        cnew, ctype, copen, csize, cclose = coords
        return NewExpr(element_type, size, cnew.start, csize, res_coord)

    def check(self, context):
        self.size.check(context)

        if self.size.type != Type.Int:
            raise BadNewSizeType(self.size_coord.start, self.size.type)

        self.type = ArrayType(self.element_type)

@dataclass
class BinOpExpr(Expr):
    left: Expr
    op: str
    op_coord: pe.Position
    right: Expr
    coord: pe.Fragment = None
    type: typing.Any = None

    @staticmethod
    def create(fixed_op=None):
        @pe.ExAction
        def action(attrs, coords, res_coord):
            if fixed_op is None:
                left, op, right = attrs
            else:
                left, right = attrs
                op = fixed_op

            cleft, cop, cright = coords
            return BinOpExpr(left, op, cop.start, right, res_coord)

        return action

    def check(self, context):
        self.left.check(context)
        self.right.check(context)

        result = binary_result_type(self.left.type, self.op, self.right.type)

        if result is None:
            raise BadBinaryType(self.op_coord, self.left.type, self.op, self.right.type)

        self.type = result


@dataclass
class UnOpExpr(Expr):
    op: str
    op_coord: pe.Position
    expr: Expr
    coord: pe.Fragment = None
    type: typing.Any = None

    @staticmethod
    def create(op):
        @pe.ExAction
        def action(attrs, coords, res_coord):
            expr, = attrs
            cop, cexpr = coords
            return UnOpExpr(op, cop.start, expr, res_coord)

        return action

    def check(self, context):
        self.expr.check(context)

        if self.op == '-':
            if self.expr.type in (Type.Int, Type.Char):
                self.type = Type.Int
                return
        elif self.op == 'not':
            if self.expr.type == Type.Bool:
                self.type = Type.Bool
                return

        raise BadUnaryType(self.op_coord, self.op, self.expr.type)

# ---------- Terminals ----------

IDENT = pe.Terminal('IDENT', '[A-Za-z][A-Za-z0-9_]*', str)

FUNCNAME = pe.Terminal(
    'FUNCNAME',
    '[A-Z][A-Za-z0-9_]*(?=\\s*\\()',
    str,
)

INT_CONST = pe.Terminal(
    'INT_CONST',
    '(\\{[0-9]+\\}[0-9A-Za-z]+|[0-9]+)',
    str,
    priority=7,
)

CHAR_CONST = pe.Terminal(
    'CHAR_CONST',
    "'([^'\\n]|'')'|\\#[A-Z]+|\\#\\{[0-9A-Fa-f]+\\}",
    str,
    priority=7,
)

STRING_CONST = pe.Terminal(
    'STRING_CONST',
    '("([^"\\n])*"|\\$QUOT|\\$[A-Z]+|\\$\\{[0-9A-Fa-f]+\\})([ \\t\\r\\n]+("([^"\\n])*"|\\$QUOT|\\$[A-Z]+|\\$\\{[0-9A-Fa-f]+\\}))*',
    str,
    priority=7,
)

def make_keyword(word):
    return pe.Terminal(
        word.upper(),
        word,
        lambda _: None,
        re_flags=re.IGNORECASE,
        priority=10,
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
    lambda header, body: FunctionDef(
        header.name,
        header.name_coord,
        header.params,
        header.return_type,
        body,
    )

NFunctionHeader |= NReturnTypeOpt, FUNCNAME, '(', NFormalParamsOpt, ')', FunctionHeader.create

NReturnTypeOpt |= NoReturnType
NReturnTypeOpt |= NType

NFormalParamsOpt |= lambda: []
NFormalParamsOpt |= NFormalParams

NFormalParams |= NFormalParam, lambda p: [p]
NFormalParams |= NFormalParams, ',', NFormalParam, lambda ps, p: ps + [p]

NFormalParam |= NType, IDENT, Parameter.create

NType |= NPrimitiveType
NType |= NType, KW_ARRAY, ArrayType

NPrimitiveType |= KW_INT, lambda: Type.Int
NPrimitiveType |= KW_CHAR, lambda: Type.Char
NPrimitiveType |= KW_BOOL, lambda: Type.Bool

NStatementBlock |= lambda: StatementBlock([])
NStatementBlock |= NStatements, lambda statements: StatementBlock(statements)

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

NDeclItem |= IDENT, DeclItem.create
NDeclItem |= IDENT, ':=', NExpr, DeclItem.create

NAssignStatement |= NExpr, ':=', NExpr, AssignStatement.create

NCallStatement |= NFunctionCall, CallStatement

NIfStatement |= KW_IF, NExpr, KW_THEN, NStatementBlock, NElsifParts, NElsePartOpt, KW_END, IfStatement.create

NElsifParts |= lambda: []
NElsifParts |= NElsifParts, KW_ELSIF, NExpr, KW_THEN, NStatementBlock, IfBranch.create

NElsePartOpt |= lambda: StatementBlock([])
NElsePartOpt |= KW_ELSE, NStatementBlock, lambda body: body

NWhileStatement |= KW_WHILE, NExpr, KW_DO, NStatementBlock, KW_END, WhileStatement.create

NForStatement |= NForInit, KW_TO, NExpr, NStepOpt, KW_DO, NStatementBlock, KW_END, ForStatement.create

NForInit |= IDENT, ':=', NExpr, ForInit.create(False)
NForInit |= NType, IDENT, ':=', NExpr, ForInit.create(True)

NStepOpt |= lambda: ConstExpr('1', Type.Int)
NStepOpt |= KW_STEP, NExpr, lambda expr: expr

NDoWhileStatement |= KW_DO, NStatementBlock, KW_WHILE, NExpr, DoWhileStatement.create

NReturnStatement |= KW_RETURN, ReturnStatement.create
NReturnStatement |= KW_RETURN, NExpr, ReturnStatement.create

NAssertStatement |= KW_ASSERT, NExpr, AssertStatement.create

NExpr |= NOrExpr

NOrExpr |= NAndExpr
NOrExpr |= NOrExpr, NOrOp, NAndExpr, BinOpExpr.create()

NOrOp |= KW_OR, lambda: 'or'
NOrOp |= KW_XOR, lambda: 'xor'

NAndExpr |= NCmpExpr
NAndExpr |= NAndExpr, KW_AND, NCmpExpr, BinOpExpr.create('and')

NCmpExpr |= NAddExpr
NCmpExpr |= NAddExpr, NCmpOp, NAddExpr, BinOpExpr.create()

NCmpOp |= '=', lambda: '='
NCmpOp |= '<>', lambda: '<>'
NCmpOp |= '<', lambda: '<'
NCmpOp |= '>', lambda: '>'
NCmpOp |= '<=', lambda: '<='
NCmpOp |= '>=', lambda: '>='

NAddExpr |= NMulExpr
NAddExpr |= NAddExpr, NAddOp, NMulExpr, BinOpExpr.create()

NAddOp |= '+', lambda: '+'
NAddOp |= '-', lambda: '-'

NMulExpr |= NPowExpr
NMulExpr |= NMulExpr, NMulOp, NPowExpr, BinOpExpr.create()

NMulOp |= '*', lambda: '*'
NMulOp |= '/', lambda: '/'
NMulOp |= KW_MOD, lambda: 'mod'

NPowExpr |= NUnaryExpr
NPowExpr |= NUnaryExpr, '**', NPowExpr, BinOpExpr.create('**')

NUnaryExpr |= NPostfixExpr
NUnaryExpr |= '-', NUnaryExpr, UnOpExpr.create('-')
NUnaryExpr |= KW_NOT, NUnaryExpr, UnOpExpr.create('not')

NPostfixExpr |= NPrimaryExpr
NPostfixExpr |= NPostfixExpr, '[', NExpr, ']', IndexExpr.create

NPrimaryExpr |= IDENT, VariableExpr.create
NPrimaryExpr |= NConstant
NPrimaryExpr |= NFunctionCall
NPrimaryExpr |= KW_NEW, NType, '[', NExpr, ']', NewExpr.create
NPrimaryExpr |= '(', NExpr, ')', lambda expr: expr

NFunctionCall |= FUNCNAME, '(', NActualParamsOpt, ')', CallExpr.create

NActualParamsOpt |= lambda: []
NActualParamsOpt |= NActualParams

NActualParams |= NExpr, lambda expr: [expr]
NActualParams |= NActualParams, ',', NExpr, lambda args, expr: args + [expr]

NConstant |= INT_CONST, ConstExpr.create(Type.Int)
NConstant |= CHAR_CONST, ConstExpr.create(Type.Char)
NConstant |= STRING_CONST, ConstExpr.create(ArrayType(Type.Char))
NConstant |= KW_T, ConstExpr.create(Type.Bool, True)
NConstant |= KW_F, ConstExpr.create(Type.Bool, False)
NConstant |= KW_NULL, ConstExpr.create(None, None)

# ---------- Parser ----------

p = pe.Parser(NProgram, method=pe.EARLEY)

p.add_skipped_domain('\\s')
p.add_skipped_domain('^\\*.*')
p.add_skipped_domain('\\*\\*\\*.*')

# ---------- Main ----------

for filename in sys.argv[1:]:
    try:
        with open(filename, encoding='utf-8') as f:
            tree = p.parse(f.read())
            tree.check()
            print('Программа корректна')
    except pe.Error as e:
        print(f'Ошибка {e.pos}: {e.message}')
