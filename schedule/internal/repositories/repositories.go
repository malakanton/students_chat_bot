package repositories

import (
	"context"
	"log/slog"
	"schedule/internal/repositories/group"
	"schedule/internal/repositories/lesson"
	"schedule/internal/repositories/subject"
	"schedule/internal/repositories/teacher"
	"schedule/internal/storage"
)

type Repositories struct {
	Logger *slog.Logger
	Gr     group.Repository
	Teach  teacher.Repository
	Les    lesson.Repository
	Subj   subject.Repository
}

func SetUpRepositories(db storage.Client, ctx context.Context, logger *slog.Logger) (rep Repositories) {
	return Repositories{
		Logger: logger,
		Gr:     group.NewRepository(db, logger),
		Teach:  teacher.NewRepository(db, logger),
		Les:    lesson.NewRepository(db, logger),
		Subj:   subject.NewRepository(db, logger),
	}
}
