package parser_handler

import (
	"context"
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/render"
	"log/slog"
	"net/http"
	resp "schedule/internal/lib/api/response"
	pupl "schedule/internal/parser-uploader"
	"strconv"
)

type Response struct {
	resp.Response
}

func ParseSchedule(ctx context.Context, pu *pupl.ParserUploader) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {

		spreadSheetId := chi.URLParam(r, "spreadsheet_id")
		var err error

		id, err := strconv.Atoi(spreadSheetId)
		if err != nil || id >= 0 {
			pu.Logger.Error("invalid spreadsheet_id", slog.String("error", err.Error()))
			render.JSON(w, r, resp.Error("invalid spreadsheet_id"))
			return
		}

		err = pu.ParseAndUploadSchedule(false, id)
		if err != nil {
			render.JSON(w, r, resp.Error(err.Error()))
			return
		}
		responseOK(w, r)
	}
}

func responseOK(w http.ResponseWriter, r *http.Request) {
	render.JSON(w, r, Response{
		Response: resp.OK(),
	})
}
