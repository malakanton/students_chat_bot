package teachers

import (
	"context"
	"github.com/go-chi/chi/v5"
	"log/slog"
	"schedule/internal/http-server/handlers/teachers/parser"
	"schedule/internal/http-server/handlers/teachers/register"
	"schedule/internal/http-server/handlers/teachers/teacher-getter"
	pupl "schedule/internal/parser-uploader"

	"schedule/internal/repositories/teacher"
)

func TeacherRoutes(ctx context.Context, logger *slog.Logger, rep teacher.Repository, pu *pupl.ParserUploader) chi.Router {
	r := chi.NewRouter()
	r.Post("/register", register.RegTeacher(ctx, logger, rep))
	r.Get("/{id}", teacher_getter.GetTeacher(ctx, logger, rep))
	r.Get("/all", teacher_getter.GetTeachers(ctx, logger, rep))
	r.Get("/parse_file", parser.UploadTeachers(ctx, logger, pu))

	return r
}
