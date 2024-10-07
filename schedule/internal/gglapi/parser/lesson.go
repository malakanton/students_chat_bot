package parser

import (
	"errors"
	"fmt"
	"regexp"
	"schedule/internal/gglapi/parser/timings"
	p "schedule/internal/lib/parser-tools"
	"strings"
	"time"
)

const (
	BS        string = "Классный час"
	BsCode    string = "BS"
	NoCode    string = "NO_CODE"
	NoTeacher string = "NO_TEACHER"
)

type Lesson struct {
	DateTime    timings.LessonTime
	Cell        string
	RawString   string
	Loc         string
	WholeDay    bool
	Filial      timings.Filial
	Teacher     string // here is the teacher last name with initials, just how it is in raw schedule
	Subject     string
	SubjectCode string
	SpecialCase string
	TeacherSwap bool
	Cancelled   bool
	Modified    bool
}

func NewLesson(lessonTime timings.LessonTime, cell, rawString, loc string, wholeDay bool, filial timings.Filial) Lesson {
	return Lesson{
		Cell:      cell,
		DateTime:  lessonTime,
		RawString: rawString,
		Loc:       loc,
		WholeDay:  wholeDay,
		Filial:    filial,
		Subject:   "NO_SUBJECT",
		Teacher:   "NO_TEACHER",
	}
}

func NewSubLesson(l Lesson, subjectCode, rawString string) Lesson {
	return Lesson{
		Cell:        l.Cell,
		DateTime:    l.DateTime,
		Loc:         l.Loc,
		Filial:      l.Filial,
		Modified:    false,
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

func NewFullDayLesson(date time.Time, name, cell string) Lesson {
	return Lesson{
		Cell:      cell,
		DateTime:  timings.LessonTime{Start: date},
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
		l.DateTime.Start.Format("2006-01-02 [15:04"),
		l.DateTime.End.Format("15:04]"),
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
		l.RawString = strings.ReplaceAll(l.RawString, "ОТМЕНА", "")
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

func (l *Lesson) ParseRawString() (subLesson Lesson, err error) {
	fmt.Printf("cell:%s, raw string: %s\n", l.Cell, l.RawString)

	emptyLesson := Lesson{}
	re, _ := regexp.Compile(`\n`)
	l.RawString = re.ReplaceAllLiteralString(l.RawString, "")

	if strings.Contains(l.RawString, BS) {
		_, err = l.parseTeacher()
		l.Subject = BS
		l.SubjectCode = BsCode
		if err != nil {
			return emptyLesson, nil
		}
		return emptyLesson, nil
	}

	subLesson, err = l.parseSubjectCode()
	if err != nil {
		if err.Error() == "two lessons" {
			_, _ = subLesson.parseTeacher()

			err = subLesson.GetSubjectAndCancelled()
			if err != nil {
				return emptyLesson, err
			}
		} else {
			return emptyLesson, err
		}
	}

	swappedTeacherLesson, err := l.parseTeacher()
	if err != nil && l.Teacher != NoTeacher {
		if err.Error() == "two teachers" {
			err = swappedTeacherLesson.GetSubjectAndCancelled()
			if err != nil {
				return Lesson{}, err
			}
			subLesson = swappedTeacherLesson
		} else {
			return emptyLesson, err
		}
	}

	err = l.GetSubjectAndCancelled()
	if err != nil {
		return emptyLesson, err
	}

	err = l.parseSpecialCase()
	if err != nil {
		return emptyLesson, err
	}

	return subLesson, nil
}

func (l *Lesson) parseSubjectCode() (subLesson Lesson, err error) {
	re := regexp.MustCompile(`[А-Я]{2,4}\.\d{2,4}(\.\d{2})?(\.\d{1,2})?[а-я]?`)
	foundCodes := re.FindAllString(l.RawString, -1)
	subLesson = Lesson{}

	if foundCodes == nil {
		l.SubjectCode = NoCode
		return subLesson, nil // fmt.Errorf("no subject code found in cell %s, string: %s", l.Cell, l.RawString)
	}

	if len(foundCodes) == 1 {
		l.SubjectCode = foundCodes[0]
		return subLesson, nil
	}

	if len(foundCodes) == 2 {
		twoSubjects := strings.Split(l.RawString, foundCodes[1])

		l.SetModified()
		l.SetSubjectCode(foundCodes[0])
		l.RawString = twoSubjects[0]

		subLesson = NewSubLesson(*l, foundCodes[1], twoSubjects[1])

		return subLesson, errors.New("two lessons")
	} else {
		return subLesson, fmt.Errorf("more than 2 lessons code in cell %s, string %s", l.Cell, l.RawString)
	}
}

func (l *Lesson) parseTeacher() (subLesson Lesson, err error) {
	re := regexp.MustCompile(`([а-яА-Я]\.?-)?[А-Я][а-я]+ ( ?[А-Я]\.?){2}`)
	foundTeachers := re.FindAllString(l.RawString, -1)
	emptyLesson := Lesson{}

	if foundTeachers == nil {

		reTeacherSurName := regexp.MustCompile(`[А-Я][а-я]+`)
		teachersSurNames := reTeacherSurName.FindAllString(l.RawString, -1)
		if len(teachersSurNames) > 1 {
			l.Teacher = teachersSurNames[len(teachersSurNames)-1]
			return emptyLesson, nil
		}
		err = fmt.Errorf("no teachers names found in cell %s, string: %s", l.Cell, l.RawString)
		l.Teacher = NoTeacher
		return emptyLesson, err
	}

	if len(foundTeachers) == 1 {
		l.Teacher = prepTeacherName(foundTeachers[0])
		return emptyLesson, nil
	}

	if len(foundTeachers) == 2 {
		l.SetModified()
		l.SetCancelled()
		l.Teacher = prepTeacherName(foundTeachers[1])

		l.Subject = p.CleanUpSubjectString(l.RawString, l.SubjectCode, re)

		subLesson = NewLessonWithTeacherSwap(*l, prepTeacherName(foundTeachers[0]))

		return subLesson, errors.New("two teachers")
	} else {
		return emptyLesson, fmt.Errorf("more than 2 teachers in cell %s, string %s", l.Cell, l.RawString)
	}
}

func (l *Lesson) GetSubjectAndCancelled() (err error) {
	err = l.checkIfCancelled()
	if err != nil {
		return err
	}
	err = l.parseSubject()
	if err != nil {
		return err
	}
	return nil
}

func (l *Lesson) parseSubject() error {
	err := fmt.Errorf("No subject name in string %s, cell %s", l.RawString, l.Cell)
	reDate := regexp.MustCompile(`\d{2}\.?\d{2}`)

	subjectNoCode := strings.ReplaceAll(l.RawString, l.SubjectCode, "")
	subjectNoTeacher := strings.Split(subjectNoCode, strings.Split(l.Teacher, " ")[0])
	if len(subjectNoTeacher) == 0 {
		return err
	}

	subjectNoDate := reDate.ReplaceAllLiteralString(subjectNoTeacher[0], "")
	trimmed := strings.TrimSpace(subjectNoDate)
	re := regexp.MustCompile(`[а-яА-Я ()/]+`)
	if re.MatchString(trimmed) {
		l.Subject = trimmed
		return nil
	}
	return err
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

func prepTeacherName(s string) string {
	s = strings.ReplaceAll(s, ".-", "-")
	s = strings.ReplaceAll(s, ". ", ".")
	if !strings.HasSuffix(s, ".") {
		s = s + "."
	}
	return s
}
