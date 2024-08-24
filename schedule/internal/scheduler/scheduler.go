package scheduler

import (
	cron "github.com/robfig/cron/v3"
	"log/slog"
	pupl "schedule/internal/parser-uploader"
	"time"
	_ "time/tzdata"
)

func NewScheduler(timeZone string) (*cron.Cron, error) {
	moscowTime, err := time.LoadLocation(timeZone)
	if err != nil {
		return cron.New(), err
	}
	schd := cron.New(cron.WithLocation(moscowTime))
	return schd, err
}

func AddScheduledJobs(s *cron.Cron, pu *pupl.ParserUploader) error {
	for _, job := range pu.Cfg.Scheduler.Jobs {
		_, err := s.AddFunc(job, func() { pu.ParseAndUploadSchedule(false, -1) })
		if err != nil {
			return err
		}
		pu.Logger.Info("scheduler job added", slog.String("job", job))
	}
	return nil
}
