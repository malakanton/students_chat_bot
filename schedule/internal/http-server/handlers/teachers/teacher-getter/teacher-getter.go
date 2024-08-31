package teacher_getter

import (
	"context"
	"fmt"
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/render"
	"log/slog"
	"net/http"
	resp "schedule/internal/lib/api/response"
	"schedule/internal/repositories/teacher"
	"strconv"
)

type Response struct {
	resp.Response
	Teacher teacher.Teacher `json:"teacher,omitempty"`
}

type ResponseAll struct {
	resp.Response
	Teachers []teacher.Teacher `json:"teachers,omitempty"`
}

type TeacherGetter interface {
	FindById(ctx context.Context, id int) (teacher.Teacher, error)
	FindAll(ctx context.Context) (t []teacher.Teacher, err error)
}

func GetTeacher(ctx context.Context, log *slog.Logger, tg TeacherGetter) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {

		idStr := chi.URLParam(r, "id")
		var err error

		id, err := strconv.Atoi(idStr)
		if err != nil {
			log.Error("invalid id", slog.String("error", err.Error()))
			render.JSON(w, r, resp.Error("invalid id"))
			return
		}

		t, err := tg.FindById(ctx, id)
		if err != nil {
			log.Error("teacher doesnt exists", slog.String("error", err.Error()))
			render.JSON(w, r, resp.Error(fmt.Sprintf("teachers with id %d not found", id)))
			return
		}

		responseOK(w, r, t)
	}
}

func GetTeachers(ctx context.Context, log *slog.Logger, tg TeacherGetter) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {
		var err error

		t, err := tg.FindAll(ctx)
		if err != nil {
			render.JSON(w, r, resp.Error("failed to get all teachers"))
			return
		}

		responseAllOK(w, r, t)
	}
}

func responseOK(w http.ResponseWriter, r *http.Request, t teacher.Teacher) {
	render.JSON(w, r, Response{
		Response: resp.OK(),
		Teacher:  t,
	})
}

func responseAllOK(w http.ResponseWriter, r *http.Request, t []teacher.Teacher) {
	render.JSON(w, r, ResponseAll{
		Response: resp.OK(),
		Teachers: t,
	})
}
