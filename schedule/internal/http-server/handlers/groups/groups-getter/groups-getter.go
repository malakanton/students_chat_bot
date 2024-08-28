package groups_getter

import (
	"context"
	"fmt"
	"github.com/go-chi/render"
	"log/slog"
	"net/http"
	resp "schedule/internal/lib/api/response"
	"schedule/internal/repositories/group"
)

type Response struct {
	resp.Response
	Groups []group.Group `json:"groups,omitempty"`
}

type GroupsGetter interface {
	FindAll(ctx context.Context) (g []group.Group, err error)
}

func GetGroups(ctx context.Context, log *slog.Logger, gg GroupsGetter) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {

		g, err := gg.FindAll(ctx)
		if err != nil {
			log.Error("failed to get groups list", slog.String("error", err.Error()))
			render.JSON(w, r, resp.Error(fmt.Sprintf("no groups found")))
			return
		}

		responseOK(w, r, g)
	}
}

func responseOK(w http.ResponseWriter, r *http.Request, g []group.Group) {
	render.JSON(w, r, Response{
		Response: resp.OK(),
		Groups:   g,
	})
}
