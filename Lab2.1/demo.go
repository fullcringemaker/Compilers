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
