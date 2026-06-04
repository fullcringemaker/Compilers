## Абстрактный синтаксис L1

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