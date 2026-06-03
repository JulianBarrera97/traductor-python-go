package main

import (
	"bufio"
	"fmt"
	"os"
	"sort"
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

	n := func() int { v, _ := strconv.Atoi(_readLine()); return v }()
	a := func() []int {
		_raw := strings.Fields(_readLine())
		_result := make([]int, len(_raw))
		for _k, _v := range _raw {
			_result[_k], _ = strconv.Atoi(_v)
		}
		return _result
	}()
	sort.Ints(a)
	ans := 0
	left := 0
	for right := 0; right < n; right++ {
		for a[right] - a[left] > 5 {
			left += 1
		}
		ans = func() int { if ans > right - left + 1 { return ans }; return right - left + 1 }()
	}
	fmt.Println(ans)
}