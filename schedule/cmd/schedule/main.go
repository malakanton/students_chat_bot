package main

import (
	"log/slog"
	"os"

	"schedule/internal/config"
)

const (
	envLocal = "dev"
	envProd  = "prod"
)

func main() {
	cfg := config.MustConfig()

	logger := setupLogger(cfg.Env)

	logger.Info("Starting schedule service", slog.String("env", cfg.Env))
	logger.Debug("Debug mode is ON")

	// init logger

	// init storage

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
