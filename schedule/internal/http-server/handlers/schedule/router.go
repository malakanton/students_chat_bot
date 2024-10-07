package schedule

import (
	"context"
	"github.com/go-chi/chi/v5"
	ph "schedule/internal/http-server/handlers/schedule/parser-handler"
	sl "schedule/internal/http-server/handlers/schedule/sheets-list"
	pupl "schedule/internal/parser-uploader"
)

func ScheduleRoutes(ctx context.Context, pu *pupl.ParserUploader) chi.Router {
	r := chi.NewRouter()
	r.Get("/parse/{spreadsheet_id}", ph.ParseSchedule(ctx, pu))
	r.Get("/parse/sheets_list", sl.GetSheetsList(ctx, pu))
	return r
}
