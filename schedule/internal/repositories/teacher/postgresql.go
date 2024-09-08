package teacher

import (
	"context"
	"fmt"
	"github.com/jackc/pgx/v5/pgconn"
	"log/slog"
	"schedule/internal/config"
	"schedule/internal/storage"
)

type repository struct {
	client storage.Client
	logger *slog.Logger
	cfg    *config.Config
}

func (r *repository) Create(ctx context.Context, teacher *Teacher) error {
	q := `
INSERT INTO teachers (name, code) 
VALUES ($1, $2)
RETURNING id;
`
	teacher.SetCode(r.cfg.Settings.TeacherCodeSize)
	if err := r.client.QueryRow(ctx, q, teacher.Name, teacher.Code).Scan(&teacher.Id); err != nil {
		if pgErr, ok := err.(*pgconn.PgError); ok {
			sqlError := fmt.Errorf("SQL error occurred: %s, Where: %s, details: %s, constraint: %s", pgErr.Message, pgErr.Where, pgErr.Detail, pgErr.ConstraintName)
			r.logger.Error(sqlError.Error())
			return sqlError
		}
		return err
	}
	r.logger.Info("new teacher created: ", slog.String("name", teacher.Name))
	return nil
}

func (r *repository) FindAll(ctx context.Context) (t []Teacher, err error) {
	q := `
SELECT id, name, full_name
FROM teachers
WHERE tg_id is null
`
	rows, err := r.client.Query(ctx, q)
	if err != nil {
		return nil, err
	}

	teachers := make([]Teacher, 0)
	for rows.Next() {
		var teach Teacher

		err = rows.Scan(&teach.Id, &teach.Name, &teach.FullName)
		if err != nil {
			return nil, err
		}
		teachers = append(teachers, teach)
	}
	if err = rows.Err(); err != nil {
		return nil, err
	}
	return teachers, nil
}

func (r *repository) FindById(ctx context.Context, id int) (Teacher, error) {
	q := `
SELECT id, name, full_name, code
FROM teachers
WHERE id = $1
`
	var teach Teacher
	err := r.client.QueryRow(ctx, q, id).Scan(&teach.Id, &teach.Name, &teach.FullName, &teach.Code)
	if err != nil {
		return Teacher{}, err
	}
	return teach, nil
}

func (r *repository) FindByName(ctx context.Context, name string) (*Teacher, error) {
	q := `
SELECT id, name, code
FROM teachers
WHERE name = $1
`
	var teach Teacher
	err := r.client.QueryRow(ctx, q, name).Scan(&teach.Id, &teach.Name, &teach.Code)
	if err != nil {
		return &Teacher{}, err
	}
	return &teach, nil
}

func (r *repository) FindByCode(ctx context.Context, code string) (Teacher, error) {
	q := `
SELECT id, name
FROM teachers
WHERE code = $1
`
	var teach Teacher
	err := r.client.QueryRow(ctx, q, code).Scan(&teach.Id, &teach.Name)
	if err != nil {
		return Teacher{}, err
	}
	return teach, nil
}

func (r *repository) UpdateTgId(ctx context.Context, teacher Teacher) error {
	q := `
UPDATE teachers
SET tg_id = $1
WHERE id = $2
`
	if _, err := r.client.Exec(ctx, q, teacher.TgId, teacher.Id); err != nil {
		if pgErr, ok := err.(*pgconn.PgError); ok {
			sqlError := fmt.Errorf("SQL error occurred: %s, Where: %s, details: %s, constraint %s", pgErr.Message, pgErr.Where, pgErr.Detail, pgErr.ConstraintName)
			r.logger.Error(sqlError.Error())
			return sqlError
		}
	}
	return nil
}

func (r *repository) Delete(ctx context.Context, id string) error {
	//TODO implement me
	panic("implement me")
}

func NewRepository(client storage.Client, logger *slog.Logger, cfg *config.Config) Repository {
	return &repository{
		client: client,
		logger: logger,
		cfg:    cfg,
	}
}
