package scheduler

import (
	"context"
	cron "github.com/robfig/cron/v3"
	"log/slog"
	"schedule/internal/config"
	"schedule/internal/gglapi"
	"schedule/internal/gglapi/drive"
	"schedule/internal/gglapi/parser"
	"schedule/internal/repositories"
	"schedule/internal/uploader"
	"time"
)

func NewScheduler(timeZone string) *cron.Cron {
	moscowTime, _ := time.LoadLocation(timeZone)
	schd := cron.New(cron.WithLocation(moscowTime))
	return schd
}

func AddScheduledJobs(s *cron.Cron, cfg *config.Config, logger *slog.Logger, dp parser.DocumentParser, rep repositories.Repositories, gs *gglapi.GoogleApi, checkDate *string) error {
	for _, job := range cfg.Scheduler.Jobs {
		_, err := s.AddFunc(job, func() { ParseSchedule(logger, dp, rep, gs, checkDate) })
		if err != nil {
			return err
		}
		logger.Info("scheduler job added", slog.String("job", job))
	}
	return nil
}

func ParseSchedule(logger *slog.Logger, dp parser.DocumentParser, rep repositories.Repositories, gs *gglapi.GoogleApi, checkDate *string) {
	logger.Info("scheduled job started")

	lastModifiedDate, err := drive.GetLastModifiedDate(gs.DriveService, dp.Cfg.SpreadSheetId, dp.Cfg.Settings.TimeZone)

	if err != nil {
		logger.Error("failed to get last modified date", slog.String("err", err.Error()))
	}
	if lastModifiedDate <= *checkDate {
		return
	}

	logger.Info("spreadsheet was modified", slog.String("at", lastModifiedDate))

	parsedSchedule, err := dp.ParseDocument(-1)
	if err != nil {
		logger.Error("error occured while parsing document", slog.String("err", err.Error()))
	}

	sup := uploader.NewScheduleUploader(parsedSchedule, rep.Gr, rep.Teach, rep.Les, rep.Subj, logger)

	err = sup.UploadSchedule(context.Background())
	if err != nil {
		logger.Error("failed to upload schedule:", err.Error())
	}

	checkDate = &lastModifiedDate
}
