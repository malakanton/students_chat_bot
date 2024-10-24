package lesson

import (
	"context"
	"errors"
	"fmt"
	"github.com/agnivade/levenshtein"
	"github.com/jackc/pgx/v5"
	"schedule/internal/gglapi/parser"
	"schedule/internal/gglapi/parser/timings"
	"schedule/internal/repositories/group"
	"schedule/internal/repositories/subject"
	"schedule/internal/repositories/teacher"
	"time"
)

const numberOfAllowedMistakes = 4

type Lesson struct {
	Id          int             `json:"id"`
	Num         int             `json:"num"`
	WeekNum     int             `json:"week_num"`
	Start       time.Time       `json:"start,omitempty"`
	End         time.Time       `json:"end,omitempty"`
	Group       group.Group     `json:"group"`
	Loc         string          `json:"loc,omitempty"`
	WholeDay    bool            `json:"whole_day"`
	Filial      timings.Filial  `json:"filial,omitempty"`
	Teacher     teacher.Teacher `json:"teacher,omitempty"`
	Subject     subject.Subject `json:"subject,omitempty"`
	Modified    bool            `json:"modified,omitempty"`
	Cancelled   bool            `json:"cancelled"`
	TeacherSwap bool            `json:"teacher_swap"`
	SpecialCase string          `json:"special_case"`
	Link        string          `json:"link,omitempty"`
}

func (l *Lesson) String() string {
	return fmt.Sprintf(
		"[%d] Lesson date %s -> %s Fullday:%v Filial:%d Loc:%s Teacher:%s %s (swap:%v) Subject:[%s]%s Modified:%v Cancelled:%v, GroupId %d",
		l.Id,
		l.Start.Format("2006-01-02 [15:04"),
		l.End.Format("15:04]"),
		l.WholeDay,
		l.Filial,
		l.Loc,
		l.Teacher.LastName,
		l.Teacher.Initials,
		l.TeacherSwap,
		l.Subject.Code,
		l.Subject.Name,
		l.Modified,
		l.Cancelled,
		l.Group.Id,
	)
}

func NewLessonFromParsed(lesson *parser.Lesson, gr *parser.Group, weekNum int) Lesson {
	return Lesson{
		WeekNum:     weekNum,
		Num:         lesson.DateTime.Num,
		Start:       lesson.DateTime.Start,
		End:         lesson.DateTime.End,
		Group:       group.Group{Name: gr.Name, StudyForm: gr.StudyForm},
		Loc:         lesson.Loc,
		WholeDay:    lesson.WholeDay,
		Filial:      lesson.Filial,
		Teacher:     teacher.NewTeacherFromParsed(lesson.Teacher),
		Subject:     subject.Subject{Name: lesson.Subject, Code: lesson.SubjectCode},
		Modified:    lesson.Modified,
		SpecialCase: lesson.SpecialCase,
		TeacherSwap: lesson.TeacherSwap,
		Cancelled:   lesson.Cancelled,
	}
}

func (l *Lesson) SetTeacher(ctx context.Context, rep teacher.Repository, t *teacher.Teacher) (err error) {
	const op = "lessons.model.set_teacher"
	var (
		existingTeacher *teacher.Teacher
		found           bool
	)
	fmt.Printf("teacher: %s %s (%s %s)\n", t.LastName, t.Initials, t.FirstName, t.FathersName)
	existingTeacher, err = rep.FindByLastNameAndInitials(ctx, t)
	fmt.Printf("existing teacher: %s %s (%s %s)\n", existingTeacher.LastName, existingTeacher.Initials, existingTeacher.FirstName, existingTeacher.FathersName)
	if err != nil {
		// if there is no full match
		if errors.Is(err, pgx.ErrNoRows) {

			allTeachers, err := rep.FindAll(ctx)
			if err != nil {
				return fmt.Errorf("%s: execute statement: %w", op, err)
			}

			existingTeacher, found, err = findMistakenTeacher(t, allTeachers)
			fmt.Printf("found %v: %s %s\n", found, existingTeacher.LastName, existingTeacher.Initials)
			if err != nil || !found {
				err = rep.Create(ctx, t)
				if err != nil {
					return fmt.Errorf("%s: execute statement: %w", op, err)
				}
				return nil
			}

			t.SetId(existingTeacher.Id)
			return nil
		}

		return fmt.Errorf("%s: execute statement: %w", op, err)
	}

	t.SetId(existingTeacher.Id)
	return nil
}

func (l *Lesson) SetGroup(ctx context.Context, rep group.Repository, group *group.Group) (err error) {
	const op = "lessons.model.set_group"
	existingGroup, err := rep.FindOne(ctx, group.Name)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			err = rep.Create(ctx, group)
			if err != nil {
				return fmt.Errorf("%s: execute statement: %w", op, err)
			}
			return nil
		}
		return fmt.Errorf("%s: execute statement: %w", op, err)
	}
	group.SetIdAndCourse(existingGroup.Id, existingGroup.Course)
	return nil
}

func (l *Lesson) SetSubject(ctx context.Context, rep subject.Repository, subject *subject.Subject) (err error) {
	const op = "lessons.model.set_subject"
	if subject.Code == "" {
		subject.Code = "NO_SUBJECT"
	}
	existingSubj, err := rep.FindOne(ctx, subject.Name)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			err = rep.Create(ctx, subject)
			if err != nil {
				return fmt.Errorf("%s: execute statement: %w", op, err)
			}
			return nil
		}
		return fmt.Errorf("%s: execute statement: %w", op, err)
	}
	subject.SetIdAndCode(existingSubj.Id, existingSubj.Code)
	return nil
}

func (l *Lesson) Equals(l2 *Lesson) bool {
	return l.Teacher.Id == l2.Teacher.Id &&
		l.Subject.Id == l2.Subject.Id &&
		l.Loc == l2.Loc
}

func findMistakenTeacher(t *teacher.Teacher, allTeachers []teacher.Teacher) (existingTeacher *teacher.Teacher, found bool, err error) {
	for _, teacherCandidate := range allTeachers {
		if same := compareTwoTeachers(t.LastNameAndInitials(), teacherCandidate.LastNameAndInitials()); same {
			return &teacherCandidate, true, nil
		}
	}
	return &teacher.Teacher{}, false, nil
}

func compareTwoTeachers(t1, t2 string) bool {
	//rune1 := []rune(t1)
	//rune2 := []rune(t2)
	//
	//var mistakes int
	//for i, j := 0, 0; i < len(rune1) && j < len(rune2); j++ {
	//	if rune1[i] == rune2[j] {
	//		i++
	//		continue
	//	}
	//
	//	mistakes++
	//}
	//if mistakes < 6 {
	//	fmt.Printf("comparing teachers: %s == %s, mistakes: %d\n", t1, t2, mistakes)
	//}

	mistakes := levenshtein.ComputeDistance(t1, t2)

	return mistakes <= numberOfAllowedMistakes
}
