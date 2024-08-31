package group

import (
	"schedule/internal/gglapi/parser"
	"strconv"
)

type Group struct {
	Id        int              `json:"id"`
	Name      string           `json:"name"`
	Course    int              `json:"course"`
	StudyForm parser.StudyForm `json:"study_form"`
}

func (g *Group) SetCourse() error {
	runes := []rune(g.Name)
	var course string
	for i := 0; i < len(runes); i++ {
		if runes[i] == '-' {
			course = string(runes[i+1])
			break
		}
	}
	courseInt, err := strconv.Atoi(course)
	if err != nil {
		return err
	}
	g.Course = courseInt
	return nil
}

func (g *Group) SetIdAndCourse(id, course int) {
	g.Id = id
	g.Course = course
}
