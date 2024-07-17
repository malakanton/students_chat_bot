package main

import (
	"context"
	"fmt"
	"log/slog"
	"os"
	"schedule/internal/config"
	"schedule/internal/gglapi"
	"schedule/internal/gglapi/parser"
	"schedule/internal/storage"
)

const (
	envLocal = "dev"
	envProd  = "prod"
)

func main() {
	cfg := config.MustConfig()
	fmt.Println(cfg)
	logger := setupLogger(cfg.Env)

	logger.Info("Starting schedule service", slog.String("env", cfg.Env))
	logger.Debug("Debug mode is ON")

	db, err := storage.NewClient(context.Background(), cfg.Storage)
	fmt.Println(db)
	if err != nil {
		logger.Error("Failed to init Postgres")
	}
	logger.Info("Storage Initialised successfully")

	gs, err := gglapi.NewGglApiClient(cfg.GoogleConfig.GoogleCredsPath)
	if err != nil {
		return
	}

	parser.ParseDocument(gs, cfg)

	// init gglapi sheets client

	// init router

	// run server

	//write business logic
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
