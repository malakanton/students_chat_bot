package lesson

import (
	"schedule/internal/repositories/teacher"
	"time"
)

type GroupLessonDto struct {
	Num         int                `json:"num"`
	Start       time.Time          `json:"start"`
	End         time.Time          `json:"end"`
	Teacher     teacher.TeacherDTO `json:"teacher"`
	SubjectName string             `json:"subj"`
	Loc         string             `json:"loc"`
	Link        string             `json:"link,omitempty"`
	WholeDay    bool               `json:"whole_day"`
	SpecialCase string             `json:"special_case,omitempty"`
	Cancelled   bool               `json:"cancelled"`
}

func NewGroupLessonDto(lesson *Lesson) GroupLessonDto {
	return GroupLessonDto{
		Num:         lesson.Num,
		Start:       lesson.Start,
		End:         lesson.End,
		Teacher:     teacher.NewTeacherDto(&lesson.Teacher),
		SubjectName: lesson.Subject.Name,
		Loc:         lesson.Loc,
		Link:        lesson.Link,
		WholeDay:    lesson.WholeDay,
		SpecialCase: lesson.SpecialCase,
		Cancelled:   lesson.Cancelled,
	}
}

type TeacherLessonDto struct {
	Num         int       `json:"num"`
	Start       time.Time `json:"start"`
	End         time.Time `json:"end"`
	GroupName   string    `json:"group_name"`
	SubjectName string    `json:"subj"`
	Loc         string    `json:"loc"`
	SpecialCase string    `json:"special_case,omitempty"`
	Cancelled   bool      `json:"cancelled"`
	TeacherSwap bool      `json:"teacher_swap"`
}

func NewTeacherLessonDto(lesson *Lesson) TeacherLessonDto {
	return TeacherLessonDto{
		Num:         lesson.Num,
		Start:       lesson.Start,
		End:         lesson.End,
		GroupName:   lesson.Group.Name,
		SubjectName: lesson.Subject.Name,
		Loc:         lesson.Loc,
		SpecialCase: lesson.SpecialCase,
		Cancelled:   lesson.Cancelled,
		TeacherSwap: lesson.TeacherSwap,
	}
}
