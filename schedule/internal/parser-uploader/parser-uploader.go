package parser_uploader

import (
	"context"
	"fmt"
	"log/slog"
	"schedule/internal/config"
	"schedule/internal/gglapi"
	"schedule/internal/gglapi/drive"
	"schedule/internal/gglapi/parser"
	"schedule/internal/repositories"
	"schedule/internal/uploader"
	"time"
)

func NewParserUploader(cfg *config.Config, logger *slog.Logger, rep *repositories.Repositories, dp *parser.DocumentParser, gs *gglapi.GoogleApi) *ParserUploader {
	currDate := time.Now().Format(drive.DateLayout)
	pu := ParserUploader{
		Cfg:      cfg,
		Logger:   logger,
		Rep:      rep,
		Dp:       dp,
		Gs:       gs,
		LastDate: &currDate,
	}
	return &pu
}

type ParserUploader struct {
	Cfg      *config.Config
	Logger   *slog.Logger
	Rep      *repositories.Repositories
	Dp       *parser.DocumentParser
	Gs       *gglapi.GoogleApi
	LastDate *string
}

func (pu *ParserUploader) ParseAndUploadSchedule(scheduled bool, id int) (err error) {
	var lastModifiedDate string

	if scheduled {
		pu.Logger.Info("scheduled job started")

		lastModifiedDate, err := drive.GetLastModifiedDate(pu.Gs.DriveService, pu.Dp.Cfg.SpreadSheetId, pu.Dp.Cfg.Settings.TimeZone)

		if err != nil {
			pu.Logger.Error("failed to get last modified date", slog.String("err", err.Error()))
			return fmt.Errorf("failed to get last modified date %s", err.Error())
		}
		if lastModifiedDate <= *pu.LastDate {
			return fmt.Errorf("the spradsheet wasnt modified, last modification date is %s", lastModifiedDate)
		}

		pu.Logger.Info("spreadsheet was modified", slog.String("at", lastModifiedDate))
	}

	parsedSchedule, err := pu.Dp.ParseDocument(id)
	if err != nil {
		pu.Logger.Error("error occured while parsing document", slog.String("err", err.Error()))
		return fmt.Errorf("error occured while parsing document: %s", err.Error())
	}

	sup := uploader.NewScheduleUploader(parsedSchedule, *pu.Rep, pu.Logger)

	err = sup.UploadSchedule(context.Background())
	if err != nil {
		pu.Logger.Error("failed to upload schedule:", err.Error())
		return fmt.Errorf("failed to upload schedule: %s", err.Error())
	}

	if scheduled {
		pu.LastDate = &lastModifiedDate
	}
	return nil
}