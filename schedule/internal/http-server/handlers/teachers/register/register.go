package register

import (
	"context"
	"errors"
	"github.com/go-chi/render"
	"io"
	"log/slog"
	"net/http"
	"schedule/internal/http-server/handlers/teachers/teacher-getter"
	resp "schedule/internal/lib/api/response"
	"schedule/internal/repositories/teacher"
)

type Request struct {
	TgId int64 `json:"tg_id"`
	Id   int   `json:"teacher_id"`
}

type Register interface {
	FindById(ctx context.Context, id int) (teacher.Teacher, error)
	UpdateTgId(ctx context.Context, t teacher.Teacher) error
}

func RegTeacher(ctx context.Context, log *slog.Logger, reg Register) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {

		var req Request
		var err error

		err = render.DecodeJSON(r.Body, &req)

		if errors.Is(err, io.EOF) {
			log.Error("request body is empty")

			render.JSON(w, r, resp.Error("empty request"))

			return
		}

		if err != nil {
			log.Error("failed to decode request body", slog.String("error", err.Error()))

			render.JSON(w, r, resp.Error("failed to decode request"))

			return
		}

		log.Info("request body decoded", slog.Any("request", req))

		t, err := reg.FindById(ctx, req.Id)
		if err != nil {
			render.JSON(w, r, resp.Error("invalid teacher id"))
			return
		}

		t.SetTgId(req.TgId)

		err = reg.UpdateTgId(ctx, t)
		if err != nil {
			render.JSON(w, r, resp.Error("failed to update teachers id"))

			return
		}

		responseOK(w, r, t)
	}
}

func responseOK(w http.ResponseWriter, r *http.Request, t teacher.Teacher) {
	render.JSON(w, r, teacher_getter.Response{
		Response: resp.OK(),
		Teacher:  t,
	})
}
