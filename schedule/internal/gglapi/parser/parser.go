package parser

import (
	"errors"
	"fmt"
	"google.golang.org/api/sheets/v4"
	"log/slog"
	"schedule/internal/config"
	"schedule/internal/gglapi/document"
	pt "schedule/internal/lib/parser-tools"
)

type DocumentParser struct {
	gs     *sheets.Service
	Cfg    *config.Config
	logger *slog.Logger
}

func NewDocumentParser(gs *sheets.Service, cfg *config.Config, logger *slog.Logger) DocumentParser {
	return DocumentParser{
		gs:     gs,
		Cfg:    cfg,
		logger: logger,
	}
}

func (dp *DocumentParser) ParseDocument(id int) (s Schedule, err error) {
	d := document.NewDocument(dp.Cfg.GoogleConfig.SpreadSheetId, dp.gs)
	dp.logger.Info("start parsing document")

	err = d.GetDocumentSheetsListAndName()
	if err != nil {
		return Schedule{}, err
	}

	sheetName := d.GetSheetById(id)
	dp.logger.Info(fmt.Sprintf("working on spreadsheet \"%s\"", sheetName))

	startDate, endDate, err := pt.ExtractDatesFromSheetName(sheetName, layoutDate)
	if err != nil {
		err = fmt.Errorf("can not extract dates from sheet name: %w", err)
		return Schedule{}, err
	}

	s = NewSchedule(startDate, endDate, d.SpsheetName)

	err = s.ScheduleDates.SetYear()
	if err != nil {
		return s, err
	}

	err = s.ScheduleDates.SetDates()
	if err != nil {
		return s, err
	}

	daysColumnData, err := d.GetDaysOfweek(sheetName)
	if err != nil {
		return s, err
	}

	err = s.ParseDatesFromSlice(daysColumnData)
	if err != nil {
		return s, err
	}

	s.ScheduleDates.SetWeekNum()
	ok, err := s.ValidateDates()
	if err != nil || !ok {
		err = errors.New("failed validating the dates from sheetname and sheet data")
		return s, err
	}

	lessonsTimingsData, err := d.GetLessonsTimings(sheetName)
	if err != nil {
		return s, err
	}

	err = s.ParseLessonsTimings(lessonsTimingsData, 0)
	if err != nil {
		return s, err
	}

	scheduleData, merges, err := d.GetSheduleData(sheetName)
	if err != nil {
		return s, err
	}

	mergesMapping := pt.MakeMergesMapping(merges, int64(d.DataRowId), 2)

	err = s.ParseScheduleData(scheduleData, mergesMapping, d.DataRowId)
	if err != nil {
		return s, err
	}

	groups, lessons := s.CountGroupsLessons()
	dp.logger.Info(fmt.Sprintf("finished to parse schedule: dates %s - %s, total groups %d, total lessons %d", s.ScheduleDates.StartDate.Format(layoutFullDate), s.ScheduleDates.EndDate.Format(layoutFullDate), groups, lessons))

	return s, nil
}
