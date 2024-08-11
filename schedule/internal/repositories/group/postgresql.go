package group

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

func (r *repository) Create(ctx context.Context, group *Group) error {
	q := `
INSERT INTO groups (name, course) 
VALUES ($1, $2)
RETURNING id;
`
	if err := group.SetCourse(); err != nil {
		return err
	}

	if err := r.client.QueryRow(ctx, q, group.Name, group.Course).Scan(&group.Id); err != nil {
		if pgErr, ok := err.(*pgconn.PgError); ok {
			sqlError := fmt.Errorf("SQL error occurred: %s, Where: %s, details: %s", pgErr.Message, pgErr.Where, pgErr.Detail)
			r.logger.Error(sqlError.Error())
			return sqlError
		}
		return err
	}
	return nil
}

func (r *repository) FindAll(ctx context.Context) (s []Group, err error) {
	q := `
SELECT id, name, course
FROM groups
`
	rows, err := r.client.Query(ctx, q)
	if err != nil {
		return nil, err
	}

	subjects := make([]Group, 0)
	for rows.Next() {
		var gr Group

		err = rows.Scan(&gr.Id, &gr.Name, &gr.Course)
		if err != nil {
			return nil, err
		}
		subjects = append(subjects, gr)
	}
	if err = rows.Err(); err != nil {
		return nil, err
	}
	return subjects, nil
}

func (r *repository) FindOne(ctx context.Context, name string) (*Group, error) {
	q := `
SELECT id, name, course
FROM groups
WHERE name = $1
`
	var gr Group
	err := r.client.QueryRow(ctx, q, name).Scan(&gr.Id, &gr.Name, &gr.Course)
	if err != nil {
		return &Group{}, err
	}
	return &gr, nil
}

func (r *repository) Update(ctx context.Context, group Group) error {
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
