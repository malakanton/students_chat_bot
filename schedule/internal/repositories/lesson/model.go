package lesson

import (
	"context"
	"errors"
	"fmt"
	"github.com/jackc/pgx/v5"
	"schedule/internal/gglapi/parser"
	"schedule/internal/repositories/group"
	"schedule/internal/repositories/subject"
	"schedule/internal/repositories/teacher"
	"time"
)

type Lesson struct {
	Id          int             `json:"id"`
	WeekNum     int             `json:"week_num"`
	Start       time.Time       `json:"start,omitempty"`
	End         time.Time       `json:"end,omitempty"`
	Group       group.Group     `json:"group"`
	Loc         string          `json:"loc,omitempty"`
	WholeDay    bool            `json:"whole_day"`
	Filial      parser.Filial   `json:"filial,omitempty"`
	Teacher     teacher.Teacher `json:"teachers,omitempty"`
	Subject     subject.Subject `json:"subject,omitempty"`
	Modified    bool            `json:"modified,omitempty"`
	Cancelled   bool            `json:"cancelled"`
	TeacherSwap bool            `json:"teacher_swap"`
	SpecialCase string          `json:"special_case"`
	Link        string          `json:"link,omitempty"`
}

func (l *Lesson) String() string {
	return fmt.Sprintf(
		"[%d] Lesson date %s -> %s Fullday:%v Filial:%d Loc:%s Teacher:%s (swap:%v) Subject:[%s]%s Modified:%v Cancelled:%v",
		l.Id,
		l.Start.Format("2006-01-02 [15:04"),
		l.End.Format("15:04]"),
		l.WholeDay,
		l.Filial,
		l.Loc,
		l.Teacher.Name,
		l.TeacherSwap,
		l.Subject.Code,
		l.Subject.Name,
		l.Modified,
		l.Cancelled,
	)
}

func NewLessonFromParsed(lesson *parser.Lesson, groupName string, weekNum int) Lesson {
	return Lesson{
		WeekNum:     weekNum,
		Start:       lesson.DateTime.Start,
		End:         lesson.DateTime.End,
		Group:       group.Group{Name: groupName},
		Loc:         lesson.Loc,
		WholeDay:    lesson.WholeDay,
		Filial:      lesson.Filial,
		Teacher:     teacher.Teacher{Name: lesson.Teacher},
		Subject:     subject.Subject{Name: lesson.Subject, Code: lesson.SubjectCode},
		Modified:    lesson.Modified,
		SpecialCase: lesson.SpecialCase,
		TeacherSwap: lesson.TeacherSwap,
		Cancelled:   lesson.Cancelled,
	}
}

func (l *Lesson) SetTeacher(ctx context.Context, rep teacher.Repository, teacher *teacher.Teacher) (err error) {
	const op = "lesson.model.set_teacher"
	existingTeacher, err := rep.FindByName(ctx, teacher.Name)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			err = rep.Create(ctx, teacher)
			if err != nil {
				return fmt.Errorf("%s: execute statement: %w", op, err)
			}
			return nil
		}
		return fmt.Errorf("%s: execute statement: %w", op, err)
	}
	teacher.SetId(existingTeacher.Id)
	return nil
}

func (l *Lesson) SetGroup(ctx context.Context, rep group.Repository, group *group.Group) (err error) {
	const op = "lesson.model.set_group"
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
	const op = "lesson.model.set_subject"
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
		l.Loc == l2.Loc &&
		l.Modified == l2.Modified
}
