package lessons_getter

import (
	"context"
	"fmt"
	"github.com/go-chi/chi/v5"
	"github.com/go-chi/render"
	"log/slog"
	"net/http"
	resp "schedule/internal/lib/api/response"
	"schedule/internal/repositories/lesson"
	"strconv"
)

type ResponseTeacher struct {
	resp.Response
	Lessons []lesson.TeacherLessonDto `json:"lessons,omitempty"`
}

type ResponseGroup struct {
	resp.Response
	Lessons []lesson.GroupLessonDto `json:"lessons,omitempty"`
}

type LessonsGetter interface {
	FindWeeklyForTeacher(ctx context.Context, id, weekNum int) (lessons []lesson.TeacherLessonDto, err error)
	FindDailyForTeacher(ctx context.Context, id int, date string) (lessons []lesson.TeacherLessonDto, err error)
	FindGroupWeeklySchedule(ctx context.Context, id, weekNum int) (lessons []lesson.GroupLessonDto, err error)
	FindGroupDailySchedule(ctx context.Context, id int, date string) (lessons []lesson.GroupLessonDto, err error)
}

func TeacherWeeklySchedule(ctx context.Context, log *slog.Logger, lg LessonsGetter) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {

		idStr := chi.URLParam(r, "teacher_id")
		var err error

		id, err := strconv.Atoi(idStr)
		if err != nil {
			log.Error("invalid teacher_id", err.Error())
			render.JSON(w, r, resp.Error("invalid teacher_id"))
			return
		}

		weekNumStr := chi.URLParam(r, "week_num")

		weekNum, err := strconv.Atoi(weekNumStr)
		if err != nil {
			log.Error("invalid week_num", err.Error())
			render.JSON(w, r, resp.Error("invalid week_num"))
			return
		}

		l, err := lg.FindWeeklyForTeacher(ctx, id, weekNum)
		if err != nil {
			log.Error("no weekly schedule for week", err.Error())
			render.JSON(w, r, resp.Error(fmt.Sprintf("no lessons in week %d for teacher %d, ", weekNum, id)))
			return
		}

		responseOkTeacher(w, r, l)
	}
}

func TeacherDailySchedule(ctx context.Context, log *slog.Logger, lg LessonsGetter) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {

		idStr := chi.URLParam(r, "teacher_id")
		var err error

		id, err := strconv.Atoi(idStr)
		if err != nil {
			log.Error("invalid teacher_id", err.Error())
			render.JSON(w, r, resp.Error("invalid teacher_id"))
			return
		}

		date := chi.URLParam(r, "date")

		l, err := lg.FindDailyForTeacher(ctx, id, date)
		if err != nil {
			log.Error("no daily schedule for date", slog.String("error", err.Error()))
			render.JSON(w, r, resp.Error(fmt.Sprintf("no lessons for day %s for teacher %d, ", date, id)))
			return
		}

		responseOkTeacher(w, r, l)
	}
}

func GroupWeeklySchedule(ctx context.Context, log *slog.Logger, lg LessonsGetter) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {

		idStr := chi.URLParam(r, "group_id")
		var err error

		id, err := strconv.Atoi(idStr)
		if err != nil {
			log.Error("invalid group id", slog.String("error", err.Error()))
			render.JSON(w, r, resp.Error("invalid group id"))
			return
		}

		weekNumStr := chi.URLParam(r, "week_num")

		weekNum, err := strconv.Atoi(weekNumStr)
		if err != nil {
			log.Error("invalid week_num", err.Error())
			render.JSON(w, r, resp.Error("invalid week_num"))
			return
		}

		t, err := lg.FindGroupWeeklySchedule(ctx, id, weekNum)
		if err != nil {
			log.Error("no weekly schedule for week", err.Error())
			render.JSON(w, r, resp.Error(fmt.Sprintf("no lessons in week %d for group %d, ", weekNum, id)))
			return
		}

		responseOkGroup(w, r, t)
	}
}

func GroupDailySchedule(ctx context.Context, log *slog.Logger, lg LessonsGetter) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {

		idStr := chi.URLParam(r, "group_id")
		var err error

		id, err := strconv.Atoi(idStr)
		if err != nil {
			log.Error("invalid group id", err.Error())
			render.JSON(w, r, resp.Error("invalid group id"))
			return
		}

		date := chi.URLParam(r, "date")

		l, err := lg.FindGroupDailySchedule(ctx, id, date)
		if err != nil {
			log.Error("no daily schedule for date", err.Error())
			render.JSON(w, r, resp.Error(fmt.Sprintf("no lessons in for day %s for group %d, ", date, id)))
			return
		}

		responseOkGroup(w, r, l)
	}
}

func responseOkTeacher(w http.ResponseWriter, r *http.Request, l []lesson.TeacherLessonDto) {
	render.JSON(w, r, ResponseTeacher{
		Response: resp.OK(),
		Lessons:  l,
	})
}

func responseOkGroup(w http.ResponseWriter, r *http.Request, l []lesson.GroupLessonDto) {
	render.JSON(w, r, ResponseGroup{
		Response: resp.OK(),
		Lessons:  l,
	})
}
