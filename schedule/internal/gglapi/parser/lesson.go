package parser

import (
	"fmt"
)

type Lesson struct {
	DateTime    LessonTime
	RawString   string
	Loc         string
	WholeDay    bool
	Filial      Filial
	Teacher     string
	Subject     string
	SubjectCode string
	Modified    bool
}

func NewLesson(lessonTime LessonTime, rawString, loc string, wholeDay bool, filial Filial) Lesson {
	return Lesson{
		DateTime:    lessonTime,
		RawString:   rawString,
		Loc:         loc,
		WholeDay:    wholeDay,
		Filial:      filial,
		Teacher:     "",
		Subject:     "",
		SubjectCode: "",
		Modified:    false,
	}
}

func NewFullDayLesson(day *Day, name string) Lesson {
	return Lesson{
		DateTime:  LessonTime{start: day.Date},
		RawString: name,
		WholeDay:  true,
		Filial:    0,
	}
}

func (l *Lesson) String() string {
	return fmt.Sprintf(
		"Lesson %s-%s Fullday:%v Filial %d Loc %s Teacher %s Subject (%s) %s Modified %v",
		l.DateTime.start.Format("2006-01-02 15:04:05"),
		l.DateTime.end.Format("2006-01-02 15:04:05"),
		l.WholeDay,
		l.Filial,
		l.Loc,
		l.Teacher,
		l.SubjectCode,
		l.Subject,
		l.Modified,
	)
}
