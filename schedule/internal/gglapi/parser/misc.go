package parser

import (
	"fmt"
	"strings"
)

func makeGroupdMapping(row []interface{}) map[int]string {
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

func processLocCell(s string, even bool) (loc string, filial Filial) {
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

func mergedCellsRanges(i, j, nextDayIdx int) (cellCoord, oneLessonMerged, wholeDayMerged string) {
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
