package subject

import (
	"context"
	"fmt"
	"github.com/jackc/pgx/v5/pgconn"
	"log/slog"
	"schedule/internal/storage"
)

type repository struct {
	client storage.Client
	logger *slog.Logger
}

func (r *repository) Create(ctx context.Context, subject *Subject) error {
	q := `
INSERT INTO subjects (subject_name, code) 
VALUES ($1, $2)
RETURNING id;
`
	if err := r.client.QueryRow(ctx, q, subject.Name, subject.Code).Scan(&subject.Id); err != nil {
		if pgErr, ok := err.(*pgconn.PgError); ok {
			sqlError := fmt.Errorf("SQL error occurred: %s, Where: %s, details: %s", pgErr.Message, pgErr.Where, pgErr.Detail)
			r.logger.Error(sqlError.Error())
			return sqlError
		}
		return err
	}
	return nil
}

func (r *repository) FindAll(ctx context.Context) (s []Subject, err error) {
	q := `
SELECT id, subject_name, code
FROM subjects
`
	rows, err := r.client.Query(ctx, q)
	if err != nil {
		return nil, err
	}

	subjects := make([]Subject, 0)
	for rows.Next() {
		var subj Subject

		err = rows.Scan(&subj.Id, &subj.Name, &subj.Code)
		if err != nil {
			return nil, err
		}
		subjects = append(subjects, subj)
	}
	if err = rows.Err(); err != nil {
		return nil, err
	}
	return subjects, nil
}

func (r *repository) FindOne(ctx context.Context, code string) (*Subject, error) {
	q := `
SELECT id, subject_name
FROM subjects
WHERE code = $1
`
	var subj Subject
	err := r.client.QueryRow(ctx, q, code).Scan(&subj.Id, &subj.Name)
	if err != nil {
		return &Subject{}, err
	}
	return &subj, nil
}

func (r *repository) Update(ctx context.Context, subject Subject) error {
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
