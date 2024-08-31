package groups

import (
	"context"
	"github.com/go-chi/chi/v5"
	"log/slog"
	groups_getter "schedule/internal/http-server/handlers/groups/groups-getter"
	"schedule/internal/repositories/group"
)

func GroupsRouter(ctx context.Context, logger *slog.Logger, rep group.Repository) chi.Router {
	r := chi.NewRouter()
	r.Get("/{id}", groups_getter.GetGroups(ctx, logger, rep))

	return r
}
