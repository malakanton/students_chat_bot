package main

import (
	"context"
	"github.com/go-chi/chi/v5"
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

	"schedule/internal/http-server/handlers/groups"
	l "schedule/internal/http-server/handlers/lessons"
	schd "schedule/internal/http-server/handlers/schedule"
	t "schedule/internal/http-server/handlers/teachers"
	pupl "schedule/internal/parser-uploader"
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
	// schedule parser-handler
	dp := parser.NewDocumentParser(gs.SheetsService, cfg, logger)

	//repositories
	rep := repositories.SetUpRepositories(db, context.Background(), logger, cfg)

	sch, err := scheduler.NewScheduler(cfg.Settings.TimeZone)
	if err != nil {
		logger.Error("failed to init scheduler", err.Error())
		return
	}

	pu := pupl.NewParserUploader(cfg, logger, &rep, &dp, gs)

	defer sch.Stop()

	err = scheduler.AddScheduledJobs(sch, pu)
	if err != nil {
		logger.Error("failed to set up scheduled jobs", slog.String("err", err.Error()))
		return
	}

	go sch.Start()

	r := chi.NewRouter()

	start(r, cfg, logger, rep, pu)
}

func start(r *chi.Mux, cfg *config.Config, logger *slog.Logger, rep repositories.Repositories, pu *pupl.ParserUploader) {

	server.SetUpMiddlewares(r)
	server.SetHealthCheck(r)

	r.Mount("/teachers", t.TeacherRoutes(context.Background(), logger, rep.Teach))
	r.Mount("/lessons", l.LessonsRoutes(context.Background(), logger, rep.Les))
	r.Mount("/schedule", schd.ScheduleRoutes(context.Background(), pu))
	r.Mount("/groups", groups.GroupsRouter(context.Background(), logger, rep.Gr))

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
