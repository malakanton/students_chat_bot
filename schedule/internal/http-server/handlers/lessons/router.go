package lessons

import (
	"context"
	"github.com/go-chi/chi/v5"
	"log/slog"
	lesson_getter "schedule/internal/http-server/handlers/lessons/lessons-getter"
	"schedule/internal/repositories/lesson"
)

func LessonsRoutes(ctx context.Context, logger *slog.Logger, rep lesson.Repository) chi.Router {
	r := chi.NewRouter()
	//r.Post("/upload", register.UploadLessons(ctx, logger, rep))
	r.Get("/teacher/{teacher_id}/weekly/{week_num}", lesson_getter.TeacherWeeklySchedule(ctx, logger, rep))
	r.Get("/teacher/{teacher_id}/daily/{date}", lesson_getter.TeacherDailySchedule(ctx, logger, rep))
	r.Get("/group/{group_id}/weekly/{week_num}", lesson_getter.GroupWeeklySchedule(ctx, logger, rep))
	r.Get("/group/{group_id}/daily/{date}", lesson_getter.GroupDailySchedule(ctx, logger, rep))

	return r
}
