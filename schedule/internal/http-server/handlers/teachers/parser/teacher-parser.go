package parser

import (
	"context"
	"fmt"
	"github.com/go-chi/render"
	"log/slog"
	"net/http"
	resp "schedule/internal/lib/api/response"
	pupl "schedule/internal/parser-uploader"
)

type Response struct {
	resp.Response
	Message string `json:"message,omitempty"`
}

func UploadTeachers(ctx context.Context, log *slog.Logger, pu *pupl.ParserUploader) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {

		tp, err := pu.ParseTeachersFromExcel(ctx, log)
		if err != nil {
			render.JSON(w, r, resp.Error(fmt.Sprintf("failed to parse teachers, error: %s", err.Error())))
			return
		}
		message := fmt.Sprintf("successfully parsed %d teachers from file", len(tp.ParsedTeachersList))

		if err := pu.UploadTeachers(ctx, log, tp); err != nil {
			render.JSON(w, r, resp.Error(fmt.Sprintf("failed to upload new teachers, error: %s", err.Error())))
			return
		}

		responseOK(w, r, message)
	}
}

func responseOK(w http.ResponseWriter, r *http.Request, message string) {
	render.JSON(w, r, Response{
		Response: resp.OK(),
		Message:  message,
	})
}
