package parser

import (
	"fmt"
	"google.golang.org/api/sheets/v4"
)

func MakeMergesMapping(merges []*sheets.GridRange, startRow, startCol int64) map[string]string {
	var mapping = map[string]string{}
	for _, grid := range merges {
		key := fmt.Sprintf("%d-%d", grid.StartRowIndex-startRow, grid.StartColumnIndex-startCol)
		value := fmt.Sprintf("%d-%d", grid.EndRowIndex-startRow-1, grid.EndColumnIndex-startCol-1)
		mapping[key] = value
	}
	return mapping
}
