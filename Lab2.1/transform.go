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
