% Лабораторная работа № 2.1. Синтаксические деревья
% 18 февраля 2026 г.
% Дмитрий Трофименко, ИУ9-62Б

# Цель работы
Целью данной работы является изучение представления синтаксических деревьев в памяти компилятора и приобретение навыков преобразования синтаксических деревьев.

# Индивидуальный вариант
Заменить операторы инкремента x++ и декремента x-- на полную запись, соответственно, x = x + 1 и x = x - 1.

# Реализация

Демонстрационная программа:

```go
package main

import "fmt"

func main() {
	x := 10
	x++
	x--
	fmt.Println("x =", x)

	arr := []int{1, 2, 3}
	i := 0
	arr[i]++
	fmt.Println("arr =", arr)

	for j := 0; j < 3; j++ {
		x++
	}
	fmt.Println("x=", x)
}
```

Программа, осуществляющая преобразование синтаксического дерева:

```go
package main

import (
	"fmt"
	"go/ast"
	"go/format"
	"go/parser"
	"go/token"
	"os"
)

func rewriteStmt(s ast.Stmt) ast.Stmt {
	incdec, ok := s.(*ast.IncDecStmt)
	if !ok {
		return s
	}

	op := token.ADD
	if incdec.Tok == token.DEC {
		op = token.SUB
	}

	one := &ast.BasicLit{
		Kind:  token.INT,
		Value: "1",
	}

	return &ast.AssignStmt{
		Lhs: []ast.Expr{incdec.X},
		Tok: token.ASSIGN,
		Rhs: []ast.Expr{
			&ast.BinaryExpr{
				X:  incdec.X,
				Op: op,
				Y:  one,
			},
		},
	}
}

func rewriteBlock(block *ast.BlockStmt) {
	if block == nil {
		return
	}
	for i := range block.List {
		block.List[i] = rewriteStmt(block.List[i])
	}
}

func main() {
	inFile := os.Args[1]
	outFile := os.Args[2]

	fset := token.NewFileSet()

	file, err := parser.ParseFile(fset, inFile, nil, parser.ParseComments)
	if err != nil {
		fmt.Printf("")
		return
	}

	ast.Inspect(file, func(n ast.Node) bool {
		switch x := n.(type) {
		case *ast.BlockStmt:
			rewriteBlock(x)
		case *ast.ForStmt:
			if x.Post != nil {
				x.Post = rewriteStmt(x.Post)
			}
		}
		return true
	})

	out, err := os.Create(outFile)
	if err != nil {
		fmt.Printf("")
		return
	}
	defer out.Close()

	if err := format.Node(out, fset, file); err != nil {
		fmt.Printf("")
		return
	}
}
```

# Тестирование

Результат трансформации демонстрационной программы:

```go
package main

import "fmt"

func main() {
	x := 10
	x = x + 1
	x = x - 1
	fmt.Println("x =", x)

	arr := []int{1, 2, 3}
	i := 0
	arr[i] = arr[i] + 1
	fmt.Println("arr =", arr)

	for j := 0; j < 3; j = j + 1 {
		x = x + 1
	}
	fmt.Println("x=", x)
}
```

Вывод тестового примера на `stdout` (если необходимо)
shell
```
x = 10
arr = [2 2 3]
x= 13
```

# Вывод
