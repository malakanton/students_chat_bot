package schedule

import (
	"context"
	"github.com/go-chi/chi/v5"
	ph "schedule/internal/http-server/handlers/schedule/parser-handler"
	pupl "schedule/internal/parser-uploader"
)

func ScheduleRoutes(ctx context.Context, su *pupl.ParserUploader) chi.Router {
	r := chi.NewRouter()
	r.Get("/parse/{spreadsheet_id}", ph.ParseSchedule(ctx, su))
	return r
}
