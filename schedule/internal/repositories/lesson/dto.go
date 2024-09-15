package lesson

import "time"

type GroupLessonDto struct {
	Start       time.Time `json:"start"`
	End         time.Time `json:"end"`
	TeacherName string    `json:"teacher"`
	SubjectName string    `json:"subj"`
	Loc         string    `json:"loc"`
	Link        string    `json:"link,omitempty"`
	WholeDay    bool      `json:"whole_day"`
	SpecialCase string    `json:"special_case,omitempty"`
	Cancelled   bool      `json:"cancelled"`
}

func NewGroupLessonDto(lesson *Lesson) GroupLessonDto {
	return GroupLessonDto{
		Start:       lesson.Start,
		End:         lesson.End,
		TeacherName: lesson.Teacher.LastName,
		SubjectName: lesson.Subject.Name,
		Loc:         lesson.Loc,
		Link:        lesson.Link,
		WholeDay:    lesson.WholeDay,
		SpecialCase: lesson.SpecialCase,
		Cancelled:   lesson.Cancelled,
	}
}

type TeacherLessonDto struct {
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
