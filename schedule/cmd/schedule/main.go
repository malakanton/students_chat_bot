package main

import (
	"context"
	"github.com/go-chi/chi/v5"
	"schedule/internal/gglapi/drive"

	"log/slog"
	"net/http"
	"os"
	"os/signal"
	"schedule/internal/config"
	"schedule/internal/gglapi"
	"schedule/internal/gglapi/parser"
	"schedule/internal/http-server/server"
	"schedule/internal/repositories"
	"schedule/internal/scheduler"
	"time"

	l "schedule/internal/http-server/handlers/lessons"
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
	logger := setupLogger(cfg.Env)

	logger.Info("starting schedule service", slog.String("env", cfg.Env))
	logger.Debug("debug mode is ON")

	CheckDate := time.Now().Format(drive.DateLayout)

	// database
	db, err := storage.NewClient(context.Background(), cfg.Storage)
	if err != nil {
		logger.Error("failed to init Postgres:", err.Error())
	}
	logger.Info("storage Initialised successfully")
	_ = db
	// google api client
	gs, err := gglapi.NewGoogleApi(cfg.GoogleConfig.GoogleCredsPath)
	if err != nil {
		return
	}
	// schedule parser
	dp := parser.NewDocumentParser(gs.SheetsService, cfg, logger)

	//repositories
	rep := repositories.SetUpRepositories(db, context.Background(), logger, cfg)

	sch := scheduler.NewScheduler(cfg.Settings.TimeZone)
	defer sch.Stop()

	err = scheduler.AddScheduledJobs(sch, cfg, logger, dp, rep, gs, &CheckDate)
	if err != nil {
		logger.Error("failed to set up scheduled jobs", slog.String("err", err.Error()))
		return
	}

	go sch.Start()

	r := chi.NewRouter()

	start(r, cfg, logger, rep)
}

func start(r *chi.Mux, cfg *config.Config, logger *slog.Logger, rep repositories.Repositories) {

	server.SetUpMiddlewares(r)
	server.SetHealthCheck(r)

	r.Mount("/teachers", t.TeacherRoutes(context.Background(), logger, rep.Teach))
	r.Mount("/lessons", l.LessonsRoutes(context.Background(), logger, rep.Les))

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
