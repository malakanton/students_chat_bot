package parser_handler

import (
	"context"
	"fmt"
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/render"
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
		fmt.Println("parser handler activated")

		spreadSheetId := chi.URLParam(r, "spreadsheet_id")
		var err error

		id, err := strconv.Atoi(spreadSheetId)
		if err != nil || id >= 0 {
			pu.Logger.Error("invalid spreadsheet_id", err.Error())
			render.JSON(w, r, resp.Error("invalid spreadsheet_id"))
			return
		}

		pu.ParseAndUploadSchedule(false, id)

		responseOK(w, r)
	}
}

func responseOK(w http.ResponseWriter, r *http.Request) {
	render.JSON(w, r, Response{
		Response: resp.OK(),
	})
}
