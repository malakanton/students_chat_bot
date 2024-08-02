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

func (r *repository) Create(ctx context.Context, lesson *Lesson) error {
	q := `
INSERT INTO lessons (week_num, start_time, end_time, group_id, subject_id, teacher_id, whole_day, filial, modified, link, special_case) 
VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
RETURNING id;
`
	if _, err := r.client.Exec(ctx, q, lesson.WeekNum, lesson.Start, lesson.End, lesson.Group.Id, lesson.Subject.Id, lesson.Teacher.Id, lesson.WholeDay, lesson.Filial, lesson.Modified, lesson.Link, lesson.SpecialCase); err != nil {
		if pgErr, ok := err.(*pgconn.PgError); ok {
			sqlError := fmt.Errorf("SQL error occurred: %s, Where: %s, details: %s", pgErr.Message, pgErr.Where, pgErr.Detail)
			r.logger.Error(sqlError.Error())
			return sqlError
		}
		return err
	}
	r.logger.Info("new lesson created for group", lesson.String())
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

func (r *repository) Update(ctx context.Context, lesson Lesson) error {
	//TODO implement me
	panic("implement me")
}

func (r *repository) Delete(ctx context.Context, id string) error {
	//TODO implement me
	panic("implement me")
}

func NewRepository(client storage.Client, logger *slog.Logger) Repository {
	return &repository{
		client: client,
		logger: logger,
	}
}
