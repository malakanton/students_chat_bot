package lesson

import (
	"context"
	"fmt"
	"github.com/jackc/pgx/v5/pgconn"
	"log/slog"
	"schedule/internal/storage"
	"time"
)

type repository struct {
	client storage.Client
	logger *slog.Logger
}

func (r *repository) Update(ctx context.Context, lesson Lesson) error {
	//TODO implement me
	panic("implement me")
}

func (r *repository) Delete(ctx context.Context, id string) error {
	//TODO implement me
	panic("implement me")
}

func (r *repository) Create(ctx context.Context, lesson *Lesson) error {
	q := `
INSERT INTO lessons (week_num, start_time, end_time, group_id, subject_id, teacher_id, whole_day, loc, filial, modified, link, special_case) 
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
RETURNING id;
`
	if _, err := r.client.Exec(ctx, q, lesson.WeekNum, lesson.Start, lesson.End, lesson.Group.Id, lesson.Subject.Id, lesson.Teacher.Id, lesson.WholeDay, lesson.Loc, lesson.Filial, lesson.Modified, lesson.Link, lesson.SpecialCase); err != nil {
		if pgErr, ok := err.(*pgconn.PgError); ok {
			sqlError := fmt.Errorf("SQL error occurred: %s, Where: %s, details: %s", pgErr.Message, pgErr.Where, pgErr.Detail)
			r.logger.Error(sqlError.Error())
			return sqlError
		}
		return err
	}
	r.logger.Info("new lessons created for group", slog.String("lessons", lesson.String()))
	return nil
}

func (r *repository) FindAll(ctx context.Context) (l []Lesson, err error) {
	//TODO implement me
	panic("implement me")
}

func (r *repository) FindOne(ctx context.Context, groupName string, startTime time.Time) (Lesson, error) {
	q := `
SELECT l.id, l.start_time, l.end_time, l.group_id, l.teacher_id, l.modified
FROM lessons l
	LEFT JOIN groups g
		on l.group_id = g.id
WHERE g.name = $1 
AND l.start_time = $2
`
	var l Lesson
	if err := r.client.QueryRow(ctx, q, groupName, startTime).Scan(&l.Id, &l.Start, &l.End, &l.Group.Id, &l.Teacher.Id, &l.Modified); err != nil {
		return Lesson{}, err
	}
	return l, nil
}

func (r *repository) FindWeeklyForTeacher(ctx context.Context, id, weekNum int) (lessons []TeacherLessonDto, err error) {
	q := `
SELECT 
    l.start_time, 
    l.end_time,
    l.loc,
    g.name,
    s.subject_name,
    l.filial,
    l.cancelled,
    l.special_case
FROM lessons l 
	LEFT JOIN groups g ON g.id = l.group_id
	LEFT JOIN subjects s ON s.id = l.subject_id
WHERE l.teacher_id = $1
AND l.week_num = $2
`
	rows, err := r.client.Query(ctx, q, id, weekNum)
	if err != nil {
		return nil, err
	}

	lessons = make([]TeacherLessonDto, 0)
	for rows.Next() {
		var l Lesson

		err = rows.Scan(&l.Start, &l.End, &l.Loc, &l.Group.Name, &l.Subject.Name, &l.Filial, &l.Cancelled, &l.SpecialCase)
		if err != nil {
			return nil, err
		}
		dto := NewTeacherLessonDto(&l)
		lessons = append(lessons, dto)
	}
	if err = rows.Err(); err != nil {
		return nil, err
	}
	return lessons, nil
}

func (r *repository) FindDailyForTeacher(ctx context.Context, id int, date string) (lessons []TeacherLessonDto, err error) {
	q := `
SELECT 
    l.start_time, 
    l.end_time,
    l.loc,
    g.name,
    s.subject_name,
    l.filial,
    l.cancelled,
    l.special_case
FROM lessons l 
	LEFT JOIN groups g ON g.id = l.group_id
	LEFT JOIN subjects s ON s.id = l.subject_id
WHERE l.teacher_id = $1
AND to_char(start_time, 'yyyy-mm-dd') = $2
`
	rows, err := r.client.Query(ctx, q, id, date)
	if err != nil {
		return nil, err
	}

	lessons = make([]TeacherLessonDto, 0)
	for rows.Next() {
		var l Lesson

		err = rows.Scan(&l.Start, &l.End, &l.Loc, &l.Group.Name, &l.Subject.Name, &l.Filial, &l.Cancelled, &l.SpecialCase)
		if err != nil {
			return nil, err
		}
		dto := NewTeacherLessonDto(&l)
		lessons = append(lessons, dto)
	}
	if err = rows.Err(); err != nil {
		return nil, err
	}
	return lessons, nil
}

func (r *repository) FindGroupWeeklySchedule(ctx context.Context, id, weekNum int) (lessons []GroupLessonDto, err error) {
	q := `
SELECT 
    l.start_time, 
    l.end_time,
    l.loc,
    t.last_name,
    t.initials,
    s.subject_name,
    l.filial,
    l.cancelled,
    l.special_case,
    l.link
FROM lessons l 
	LEFT JOIN groups g ON g.id = l.group_id
    LEFT JOIN teachers t on t.id = l.teacher_id
	LEFT JOIN subjects s ON s.id = l.subject_id
WHERE l.group_id = $1
AND l.week_num = $2
`
	rows, err := r.client.Query(ctx, q, id, weekNum)
	if err != nil {
		return nil, err
	}

	lessons = make([]GroupLessonDto, 0)
	for rows.Next() {
		var l Lesson

		err = rows.Scan(&l.Start, &l.End, &l.Loc, &l.Teacher.LastName, &l.Teacher.Initials, &l.Subject.Name, &l.Filial, &l.Cancelled, &l.SpecialCase, &l.Link)
		if err != nil {
			return nil, err
		}
		dto := NewGroupLessonDto(&l)
		lessons = append(lessons, dto)
	}
	if err = rows.Err(); err != nil {
		return nil, err
	}
	return lessons, nil
}

func (r *repository) FindGroupDailySchedule(ctx context.Context, id int, date string) (lessons []GroupLessonDto, err error) {
	q := `
SELECT 
    l.start_time, 
    l.end_time,
    l.loc,
    t.last_name,
    t.initials,
    s.subject_name,
    l.filial,
    l.cancelled,
    l.special_case,
    l.link
FROM lessons l 
    LEFT JOIN teachers t on t.id = l.teacher_id
	LEFT JOIN subjects s ON s.id = l.subject_id
WHERE l.group_id = $1
AND to_char(start_time, 'yyyy-mm-dd') = $2
`
	rows, err := r.client.Query(ctx, q, id, date)
	if err != nil {
		return nil, err
	}

	lessons = make([]GroupLessonDto, 0)
	for rows.Next() {
		var l Lesson

		err = rows.Scan(&l.Start, &l.End, &l.Loc, &l.Teacher.LastName, &l.Teacher.Initials, &l.Subject.Name, &l.Filial, &l.Cancelled, &l.SpecialCase, &l.Link)
		if err != nil {
			return nil, err
		}
		dto := NewGroupLessonDto(&l)
		lessons = append(lessons, dto)
	}
	if err = rows.Err(); err != nil {
		return nil, err
	}
	return lessons, nil
}

func NewRepository(client storage.Client, logger *slog.Logger) Repository {
	return &repository{
		client: client,
		logger: logger,
	}
}
