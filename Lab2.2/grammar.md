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
