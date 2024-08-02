package parser

import (
	"errors"
	"fmt"
	"regexp"
	p "schedule/internal/lib/parser-tools"
	"strings"
)

const (
	BS     string = "Классный час"
	BsCode string = "BS"
)

type Lesson struct {
	DateTime    LessonTime
	Cell        string
	RawString   string
	Loc         string
	WholeDay    bool
	Filial      Filial
	Teacher     string
	Subject     string
	SubjectCode string
	SpecialCase string
	TeacherSwap bool
	Cancelled   bool
	Modified    bool
}

func NewLesson(lessonTime LessonTime, cell, rawString, loc string, wholeDay bool, filial Filial) Lesson {
	return Lesson{
		Cell:      cell,
		DateTime:  lessonTime,
		RawString: rawString,
		Loc:       loc,
		WholeDay:  wholeDay,
		Filial:    filial,
	}
}

func NewModifiedLesson(l Lesson, subjectCode, rawString string) Lesson {
	return Lesson{
		Cell:        l.Cell,
		DateTime:    l.DateTime,
		Loc:         l.Loc,
		Filial:      l.Filial,
		Modified:    true,
		SubjectCode: subjectCode,
		RawString:   rawString,
	}
}

func NewLessonWithTeacherSwap(l Lesson, teacherName string) Lesson {
	return Lesson{
		Cell:        l.Cell,
		DateTime:    l.DateTime,
		Loc:         l.Loc,
		Filial:      l.Filial,
		Modified:    true,
		SubjectCode: l.SubjectCode,
		TeacherSwap: true,
		RawString:   l.RawString,
		Teacher:     teacherName,
	}
}

func NewFullDayLesson(day *Day, name, cell string) Lesson {
	return Lesson{
		Cell:      cell,
		DateTime:  LessonTime{start: day.Date},
		RawString: name,
		Subject:   name,
		WholeDay:  true,
		Filial:    0,
	}
}

func (l *Lesson) String() string {
	return fmt.Sprintf(
		"[%s] Lesson date %s -> %s Fullday:%v Filial:%d Loc:%s Teacher:%s (swap:%v) Subject:[%s]%s Modified:%v Cancelled:%v",
		l.Cell,
		l.DateTime.start.Format("2006-01-02 [15:04"),
		l.DateTime.end.Format("15:04]"),
		l.WholeDay,
		l.Filial,
		l.Loc,
		l.Teacher,
		l.TeacherSwap,
		l.SubjectCode,
		l.Subject,
		l.Modified,
		l.Cancelled,
	)
}

func (l *Lesson) checkIfCancelled() error {
	if strings.Contains(l.RawString, "ОТМЕНА") {
		l.Cancelled = true
	}
	return nil
}

func (l *Lesson) SetModified() {
	l.Modified = true
}

func (l *Lesson) SetCancelled() {
	l.Cancelled = true
}

func (l *Lesson) SetSubjectCode(code string) {
	l.SubjectCode = code
}

func (l *Lesson) ParseRawString() (modifiedLesson Lesson, err error) {

	re, _ := regexp.Compile(`\n`)
	l.RawString = re.ReplaceAllLiteralString(l.RawString, "")

	if strings.Contains(l.RawString, BS) {
		_, err = l.parseTeacher()
		l.Subject = BS
		l.SubjectCode = BsCode
		if err != nil {
			return Lesson{}, nil
		}
		return Lesson{}, nil
	}

	modifiedLesson, err = l.parseSubjectCode()
	if err != nil && err.Error() == "two lessons" {
		_, err := modifiedLesson.parseTeacher()
		if err != nil {
			return Lesson{}, err
		}
		err = modifiedLesson.GetSubjectAndCancelled()
		if err != nil {
			return Lesson{}, err
		}
	}

	swappedTeacherLesson, err := l.parseTeacher()
	if err != nil {
		if err.Error() == "two teachers" {
			return swappedTeacherLesson, nil
		}
		return Lesson{}, err
	}

	err = l.GetSubjectAndCancelled()

	_ = l.parseSpecialCase()

	return modifiedLesson, nil
}

func (l *Lesson) parseSubjectCode() (modifiedLesson Lesson, err error) {
	re := regexp.MustCompile(`[А-Я]{2,4}\.\d{2,4}(\.\d{2})?[а-я]?`)
	foundCodes := re.FindAllString(l.RawString, -1)
	modifiedLesson = Lesson{}

	if foundCodes == nil {
		return modifiedLesson, fmt.Errorf("no subject code found in cell %s, string: %s", l.Cell, l.RawString)
	}

	if len(foundCodes) == 1 {
		l.SubjectCode = foundCodes[0]
		return modifiedLesson, nil
	}

	if len(foundCodes) == 2 {
		twoSubjects := strings.Split(l.RawString, foundCodes[1])

		l.SetModified()
		l.SetSubjectCode(foundCodes[1])

		modifiedLesson = NewModifiedLesson(*l, foundCodes[0], twoSubjects[1])

		return modifiedLesson, errors.New("two lessons")
	} else {
		return modifiedLesson, fmt.Errorf("more than 2 lesson code in cell %s, string %s", l.Cell, l.RawString)
	}
}

func (l *Lesson) parseTeacher() (modifiedLesson Lesson, err error) {
	re := regexp.MustCompile(`([а-яА-Я]\.?-)?[а-яА-Я][а-я]+ ( ?[А-Я]\.?){2}`)
	foundTeachers := re.FindAllString(l.RawString, -1)

	if foundTeachers == nil {

		reTeacherSurName := regexp.MustCompile(`[А-Я][а-я]+`)
		teachersSurNames := reTeacherSurName.FindAllString(l.RawString, -1)
		if len(teachersSurNames) > 1 {
			l.Teacher = teachersSurNames[len(teachersSurNames)-1]
			return Lesson{}, nil
		}
		err = fmt.Errorf("no teachers names found in cell %s, string: %s", l.Cell, l.RawString)
		return Lesson{}, err
	}

	if len(foundTeachers) == 1 {
		l.Teacher = foundTeachers[0]
		return Lesson{}, nil
	}

	if len(foundTeachers) == 2 {
		l.SetModified()
		l.SetCancelled()
		l.Teacher = foundTeachers[1]

		l.Subject = p.CleanUpSubjectString(l.RawString, l.SubjectCode, re)

		modifiedLesson = NewLessonWithTeacherSwap(*l, foundTeachers[0])

		return modifiedLesson, errors.New("two teachers")
	} else {
		return Lesson{}, fmt.Errorf("more than 2 teachers in cell %s, string %s", l.Cell, l.RawString)
	}
}

func (l *Lesson) GetSubjectAndCancelled() (err error) {
	err = l.parseSubject()
	if err != nil {
		return err
	}
	err = l.checkIfCancelled()
	if err != nil {
		return err
	}
	return nil
}

func (l *Lesson) parseSubject() error {
	splitted := strings.Split(l.RawString, l.SubjectCode)
	if len(splitted) > 1 {
		subjectNoTeacher := strings.ReplaceAll(splitted[1], l.Teacher, "")
		l.Subject = strings.TrimSpace(subjectNoTeacher)
		return nil
	}
	return fmt.Errorf("Now subject name in string %s, cell %s", l.RawString, l.Cell)
}

func (l *Lesson) parseSpecialCase() error {
	splitted := strings.Split(l.RawString, l.Teacher)
	if len(splitted) > 1 {
		re := regexp.MustCompile(`([А-Я]{2,15}\.? ?){1,3}`)
		specialcase := re.FindAllString(splitted[1], -1)
		if specialcase != nil {
			l.SpecialCase = strings.TrimSpace(specialcase[0])
		}
	}
	return nil
}
