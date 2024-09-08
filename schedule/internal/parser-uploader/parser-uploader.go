package parser_uploader

import (
	"context"
	"fmt"
	"log/slog"
	"schedule/internal/config"
	"schedule/internal/excel-parser/excel"
	"schedule/internal/gglapi"
	"schedule/internal/gglapi/drive"
	"schedule/internal/gglapi/parser"
	"schedule/internal/repositories"
	"schedule/internal/uploader"
	"time"
)

const (
	scheduleFilePath = "./tmp/curr_schedule.xlsx"
)

func NewParserUploader(cfg *config.Config, logger *slog.Logger, rep *repositories.Repositories, dp *parser.DocumentParser, gs *gglapi.GoogleApi) *ParserUploader {
	currDate := time.Now().Format(drive.DateLayout)
	pu := ParserUploader{
		Cfg:      cfg,
		Logger:   logger,
		Rep:      rep,
		Dp:       dp,
		Ed:       excel.NewExcelDocument(scheduleFilePath),
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
	Ed       *excel.ExcelDocument
	Gs       *gglapi.GoogleApi
	LastDate *string
}

func (pu *ParserUploader) ParseAndUploadScheduleFromExcel(scheduled bool, id int) (err error) {

	pu.Logger.Info("start parsing job")
	err = drive.DownloadFile(pu.Gs.DriveService, pu.Cfg.SpreadSheetId, scheduleFilePath)
	if err != nil {
		pu.Logger.Error(err.Error())
		return err
	}

	err = pu.Ed.ReadExcelFile()
	if err != nil {
		pu.Logger.Error("failed to read excel file", slog.String("err", err.Error()))
		return err
	}

	err = pu.Ed.ParseSheetData(id)
	if err != nil {
		pu.Logger.Error("failed to parse schedule data", slog.String("err", err.Error()))
		return err
	}

	return nil

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
	//teachersCounter := make(map[string]int)
	//for _, groupLessons := range parsedSchedule.GroupsSchedule {
	//	for _, lesson := range groupLessons {
	//
	//		teachersCounter[lesson.Teacher]++
	//	}
	//}
	//for teacher, count := range teachersCounter {
	//	fmt.Println(teacher, count)
	//}
	//
	//return nil

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
