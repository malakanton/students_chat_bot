package parser_tools

import (
	"fmt"
	"google.golang.org/api/sheets/v4"
	"strings"
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

func MakeGroupdMapping(row []interface{}) map[int]string {
	groupMapping := make(map[int]string)
	for i, cell := range row {
		cellValue := cell.(string)
		if cellValue == "" || strings.Contains(cellValue, "ауд") || strings.Contains(cellValue, "ГРУППА") || strings.Contains(cellValue, "ДНИ") {
			continue
		}
		groupMapping[i] = strings.Trim(cellValue, " ")
	}
	return groupMapping
}

func ProcessLocCell(s string, even bool) (loc string, filial int) {
	var whenDoubleIdx int
	if even {
		whenDoubleIdx = 1
	}

	s = strings.Replace(s, "\n", " ", -1)
	switch {
	case strings.Contains(s, "с/з"):
		loc = s
	case strings.Contains(s, "/"):
		loc = strings.Split(s, "/")[whenDoubleIdx]
	default:
		loc = s
	}
	if strings.Contains(loc, "НО") || strings.Contains(loc, "АМ") {
		loc = strings.Trim(loc, "НО")
		loc = strings.Trim(loc, "АМ")
		filial = 1
	}

	return loc, filial
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
