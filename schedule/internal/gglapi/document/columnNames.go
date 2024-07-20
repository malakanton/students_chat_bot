package document

import (
	"strings"
)

func toCharStr(i int) string {
	return string(rune('A' - 1 + i))
}

func GetExcelColumnName(n int) string {

	res := [5]string{}
	i := 0

	for n > 0 {
		remDiv := n % 26

		if remDiv == 0 {
			res[i] = "Z"
			n = n/26 - 1
		} else {
			res[i] = toCharStr(remDiv)
			n = n / 26
		}
		i++
	}
	revertedRes := revertSlice(res)
	return sliceToStr(revertedRes)
}

func sliceToStr(sl []string) string {
	return strings.Join(sl[:], "")
}

func revertSlice(sl [5]string) []string {

	var reverted []string
	for i := len(sl) - 1; i >= 0; i-- {
		reverted = append(reverted, sl[i])
	}

	return reverted
}
