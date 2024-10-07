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

func (r *repository) Create(ctx context.Context, t *Teacher) error {
	q := `
INSERT INTO teachers (last_name, first_name, fathers_name, initials, code) 
VALUES ($1, $2, $3, $4, $5)
RETURNING id;
`
	t.SetCode(r.cfg.Settings.TeacherCodeSize)
	if err := r.client.QueryRow(ctx, q, t.LastName, t.FirstName, t.FathersName, t.Initials, t.Code).Scan(&t.Id); err != nil {
		if pgErr, ok := err.(*pgconn.PgError); ok {
			sqlError := fmt.Errorf("SQL error occurred: %s, Where: %s, details: %s, constraint: %s", pgErr.Message, pgErr.Where, pgErr.Detail, pgErr.ConstraintName)
			r.logger.Error(sqlError.Error())
			return sqlError
		}
		return err
	}
	r.logger.Info("new teacher created: ", slog.String("name", fmt.Sprintf("%s %s", t.LastName, t.Initials)))
	return nil
}

func (r *repository) FindAll(ctx context.Context) (teachers []Teacher, err error) {
	q := `
SELECT id, last_name, first_name, fathers_name, initials
FROM teachers
WHERE tg_id is null
`
	rows, err := r.client.Query(ctx, q)
	if err != nil {
		return nil, err
	}

	teachers = make([]Teacher, 0)
	for rows.Next() {
		var t Teacher

		err = rows.Scan(&t.Id, &t.LastName, &t.FirstName, &t.FathersName, &t.Initials)
		if err != nil {
			return nil, err
		}
		teachers = append(teachers, t)
	}
	if err = rows.Err(); err != nil {
		return nil, err
	}
	return teachers, nil
}

func (r *repository) FindById(ctx context.Context, id int) (Teacher, error) {
	q := `
SELECT id, last_name, first_name, fathers_name, initials
FROM teachers
WHERE id = $1
`
	var t Teacher
	err := r.client.QueryRow(ctx, q, id).Scan(&t.Id, &t.LastName, &t.FirstName, &t.FathersName, &t.Initials)
	if err != nil {
		return Teacher{}, err
	}
	return t, nil
}

func (r *repository) FindByLastNameAndInitials(ctx context.Context, ti *Teacher) (*Teacher, error) {
	q := `
SELECT id, last_name, first_name, fathers_name, initials
FROM teachers
WHERE last_name = $1
AND initials = $2
`
	var t Teacher
	err := r.client.QueryRow(ctx, q, ti.LastName, ti.Initials).Scan(&t.Id, &t.LastName, &t.FirstName, &t.FathersName, &t.Initials)
	if err != nil {
		return &Teacher{}, err
	}
	return &t, nil
}

func (r *repository) FindByCode(ctx context.Context, code string) (Teacher, error) {
	q := `
SELECT id, last_name, initials
FROM teachers
WHERE code = $1
`
	var t Teacher
	err := r.client.QueryRow(ctx, q, code).Scan(&t.Id, &t.LastName, &t.Initials)
	if err != nil {
		return Teacher{}, err
	}
	return t, nil
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
