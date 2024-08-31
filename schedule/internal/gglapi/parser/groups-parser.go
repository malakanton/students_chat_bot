package parser

import (
	"regexp"
	"strings"
)

type StudyForm int

const (
	Ex StudyForm = iota
	In
)

type Group struct {
	Name      string
	StudyForm StudyForm
}

func NewGroup(name string, stForm StudyForm) Group {
	return Group{
		Name:      name,
		StudyForm: stForm,
	}
}

func MakeGroupsMapping(row []interface{}) (map[int]Group, int) {
	re := regexp.MustCompile(`[А-Я]{1,4}\d{1,2}-\d{1,3}[а-яА-Я]+`)

	groupMapping := make(map[int]Group)
	var extStudyFormTimings int
	studyForm := In

	for i, cell := range row {
		cellValue := cell.(string)
		foundGroupName := re.FindAllString(cellValue, -1)

		if len(foundGroupName) == 0 {
			if strings.Contains(cellValue, "ЗАОЧНО") {
				studyForm = Ex
				extStudyFormTimings = i
			}
			continue
		}

		g := NewGroup(foundGroupName[0], studyForm)
		groupMapping[i] = g
	}

	return groupMapping, extStudyFormTimings
}
