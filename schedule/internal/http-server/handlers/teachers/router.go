package teachers

import (
	"context"
	"github.com/go-chi/chi/v5"
	"log/slog"
	"schedule/internal/http-server/handlers/teachers/register"
	"schedule/internal/http-server/handlers/teachers/teacher-getter"
	"schedule/internal/repositories/teacher"
)

func TeacherRoutes(ctx context.Context, logger *slog.Logger, rep teacher.Repository) chi.Router {
	r := chi.NewRouter()
	r.Post("/register", register.RegTeacher(ctx, logger, rep))
	r.Get("/{id}", teacher_getter.GetTeacher(ctx, logger, rep))
	r.Get("/all", teacher_getter.GetTeachers(ctx, logger, rep))

	return r
}
