package parser_tools

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

func MergedCellsRanges(i, j, nextDayIdx int) (cellCoord, oneLessonMerged, wholeDayMerged string) {
	cellCoord = fmt.Sprintf("%d-%d", i, j)
	oneLessonMerged = fmt.Sprintf("%d-%d", i, j+1)
	wholeDayMerged = fmt.Sprintf("%d-%d", nextDayIdx-1, j+1)
	return cellCoord, oneLessonMerged, wholeDayMerged
}

func BoolToInt(b bool) int {
	if b {
		return 1
	}
	return 0
}
