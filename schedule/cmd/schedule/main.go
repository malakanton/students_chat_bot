package main

import (
	"context"
	"fmt"
	"github.com/go-chi/chi/v5"
	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"schedule/internal/config"
	"schedule/internal/gglapi"
	"schedule/internal/http-server/server"
	"schedule/internal/repositories"
	"time"

	t "schedule/internal/http-server/handlers/teachers"
	"schedule/internal/storage"
	"syscall"
)

const (
	envLocal = "dev"
	envProd  = "prod"
)

func main() {
	cfg := config.MustConfig()
	fmt.Println(cfg)
	logger := setupLogger(cfg.Env)

	logger.Info("starting schedule service", slog.String("env", cfg.Env))
	logger.Debug("debug mode is ON")

	db, err := storage.NewClient(context.Background(), cfg.Storage)
	if err != nil {
		logger.Error("failed to init Postgres:", err.Error())
	}
	logger.Info("storage Initialised successfully")
	_ = db
	gs, err := gglapi.NewGglApiClient(cfg.GoogleConfig.GoogleCredsPath)
	if err != nil {
		return
	}
	_ = gs

	rep := repositories.SetUpRepositories(db, context.Background(), logger)

	//_, err = parser.ParseDocument(gs, cfg, -2)
	//if err != nil {
	//	logger.Error("error occured:", err.Error())
	//}

	r := chi.NewRouter()

	start(r, cfg, logger, rep)
}

func start(r *chi.Mux, cfg *config.Config, logger *slog.Logger, rep repositories.Repositories) {

	server.SetUpMiddlewares(r)
	server.SetHealthCheck(r)

	r.Mount("/teachers", t.TeacherRoutes(context.Background(), logger, rep.Teach))

	logger.Info("starting server", slog.String("address", cfg.Address))

	done := make(chan os.Signal, 1)
	signal.Notify(done, os.Interrupt, syscall.SIGINT, syscall.SIGTERM)

	srv := &http.Server{
		Addr:         cfg.Address,
		Handler:      r,
		ReadTimeout:  cfg.HttpServer.Timeout,
		WriteTimeout: cfg.HttpServer.Timeout,
		IdleTimeout:  cfg.HttpServer.IdleTimeout,
	}

	go func() {
		if err := srv.ListenAndServe(); err != nil {
			logger.Error("failed to start server")
		}
	}()

	logger.Info("server started")

	<-done
	logger.Info("stopping server")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()

	if err := srv.Shutdown(ctx); err != nil {
		logger.Error("failed to stop server", err.Error())

		return
	}

	logger.Info("server stopped")
}

func setupLogger(env string) *slog.Logger {
	var log *slog.Logger

	switch env {
	case envLocal:
		log = slog.New(
			slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelDebug}),
		)
	case envProd:
		log = slog.New(
			slog.NewTextHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}),
		)
	}

	return log
}
