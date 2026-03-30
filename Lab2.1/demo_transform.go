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
