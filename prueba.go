package main

import (
	"bufio"
	"fmt"
	"os"
	"strconv"
	"strings"
)

func main() {
	_scanner := bufio.NewScanner(os.Stdin)
	_scanner.Buffer(make([]byte, 1024*1024), 1024*1024)
	_readLine := func() string {
		_scanner.Scan()
		return _scanner.Text()
	}

	inputs := strings.Fields(_readLine())
	n := func() int { v, _ := strconv.Atoi(inputs[0]); return v }()
	t := func() int { v, _ := strconv.Atoi(inputs[1]); return v }()
	s := strings.Split(strings.TrimSpace(_readLine()), "")
	for x := 0; x < t; x++ {
		i := 0
		for i < n - 1 {
			if s[i] == "B" && s[i + 1] == "G" {
				s[i], s[i + 1] = s[i + 1], s[i]
				i += 2
			} else {
				i += 1
			}
		}
	}
	aux := ""
	fmt.Println(strings.Join(s, aux))
}