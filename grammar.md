## Конкретная грамматика L1

Программа на языке L1 представляет собой набор определений функций:

```text
Program → FunctionDefs
FunctionDefs → FunctionDef
             | FunctionDefs FunctionDef
```

Определение функции состоит из заголовка и тела:

```text
FunctionDef → DEFINE FunctionHeader StatementBlock END
```

Заголовок функции начинается с `define`, затем может идти тип возвращаемого значения, после чего записываются имя функции и список формальных параметров в круглых скобках:

```text
FunctionHeader → ReturnTypeOpt IDENT '(' FormalParamsOpt ')'
ReturnTypeOpt → ε
              | Type
```

Список формальных параметров может быть пустым:

```text
FormalParamsOpt → ε
                | FormalParams
FormalParams → FormalParam
             | FormalParams ',' FormalParam
FormalParam → Type IDENT
```

Пояснение. В описании языка список параметров задаётся как последовательность объявлений, разделённых запятыми. Для конкретной грамматики удобно нормализовать это до формы `Type IDENT`, то есть один параметр на одно объявление. Это не меняет выразительную силу языка и делает грамматику однозначнее.

Типы данных:

```text
Type → PrimitiveType
     | Type ARRAY

PrimitiveType → INT
              | CHAR
              | BOOL
```

Пояснение. Постфиксное слово `array` образует массивный тип, поэтому `int array`, `char array`, `char array array` и подобные записи естественно задаются правилом `Type → Type ARRAY`. Такое устройство прямо соответствует описанию типов в L1. 

Тело функции и тела составных операторов являются последовательностями операторов, разделённых точкой с запятой:

```text
StatementBlock → ε
               | Statements

Statements → Statement
           | Statements ';' Statement
```

В языке предусмотрены девять видов операторов:

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

Оператор-объявление:

```text
DeclStatement → Type DeclItems
DeclItems → DeclItem
          | DeclItems ',' DeclItem
DeclItem → IDENT
         | IDENT ':=' Expr
```

Оператор присваивания:

```text
AssignStatement → Expr ':=' Expr
```

Пояснение. В описании языка прямо сказано, что синтаксически оператор присваивания выглядит как два выражения, разделённые `:=`. Ограничение на допустимость левой части относится уже к семантике. 

Оператор вызова функции:

```text
CallStatement → FunctionCall
```

Оператор выбора:

```text
IfStatement → IF Expr THEN StatementBlock ElsifParts ElsePartOpt END

ElsifParts → ε
           | ElsifParts ELSIF Expr THEN StatementBlock

ElsePartOpt → ε
            | ELSE StatementBlock
```

Пояснение. Такое правило покрывает все три формы из описания языка: `if ... then ... end`, `if ... then ... else ... end`, а также цепочки с `elsif`. 

Цикл с предусловием `while`:

```text
WhileStatement → WHILE Expr DO StatementBlock END
```

Цикл с предусловием в форме `to ... step ... do`:

```text
ForStatement → ForInit TO Expr StepOpt DO StatementBlock END

ForInit → IDENT ':=' Expr
        | Type IDENT ':=' Expr

StepOpt → ε
        | STEP Expr
```

Пояснение. Здесь учтено, что в языке переменная цикла может как уже существовать, так и объявляться прямо в заголовке цикла, а `step` может отсутствовать. 

Цикл с постусловием:

```text
DoWhileStatement → DO StatementBlock WHILE Expr
```

Оператор завершения функции:

```text
ReturnStatement → RETURN
                | RETURN Expr
```

Оператор-предупреждение:

```text
AssertStatement → ASSERT Expr
```

### Выражения

Общая точка входа для выражений:

```text
Expr → OrExpr
```

Самый низкий приоритет имеют `or` и `xor`:

```text
OrExpr → AndExpr
       | OrExpr OrOp AndExpr

OrOp → OR
     | XOR
```

Далее идёт `and`:

```text
AndExpr → CmpExpr
        | AndExpr AND CmpExpr
```

Операции сравнения:

```text
CmpExpr → AddExpr
        | AddExpr CmpOp AddExpr

CmpOp → '='
      | '<>'
      | '<'
      | '>'
      | '<='
      | '>='
```

Пояснение. Сравнения здесь сделаны нецепочечными, то есть в одном сравнении участвуют только два арифметических подвыражения. Это соответствует форме операций в описании языка и устраняет неоднозначность.

Сложение и вычитание:

```text
AddExpr → MulExpr
        | AddExpr AddOp MulExpr

AddOp → '+'
      | '-'
```

Умножение, деление и остаток:

```text
MulExpr → PowExpr
        | MulExpr MulOp PowExpr

MulOp → '*'
      | '/'
      | MOD
```

Возведение в степень правоассоциативно:

```text
PowExpr → UnaryExpr
        | UnaryExpr '**' PowExpr
```

Унарные операции:

```text
UnaryExpr → PostfixExpr
          | '-' UnaryExpr
          | NOT UnaryExpr
```

Пояснение. Унарный минус и `not` по таблице имеют одинаковый приоритет и выполняются справа налево, поэтому правило сделано рекурсивным вправо. 

Постфиксный уровень выражений:

```text
PostfixExpr → PrimaryExpr
            | PostfixExpr '[' Expr ']'
```

Пояснение. Так задаётся индексирование массива с наивысшим приоритетом, причём допускаются цепочки вида `a[i][j]` и индексирование результата вызова функции. Это соответствует описанию операций языка.

Первичные выражения:

```text
PrimaryExpr → IDENT
            | Constant
            | FunctionCall
            | NEW Type '[' Expr ']'
            | '(' Expr ')'
```

Вызов функции:

```text
FunctionCall → IDENT '(' ActualParamsOpt ')'

ActualParamsOpt → ε
                | ActualParams

ActualParams → Expr
             | ActualParams ',' Expr
```

Константы:

```text
Constant → INT_CONST
         | CHAR_CONST
         | STRING_CONST
         | T
         | F
         | NULL
```
