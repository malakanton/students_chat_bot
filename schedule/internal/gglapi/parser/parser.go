package parser

import (
	"errors"
	"fmt"
	"google.golang.org/api/sheets/v4"
	"schedule/internal/config"
	"schedule/internal/gglapi/document"
	"time"
)

func ParseDocument(gs *sheets.Service, cfg *config.Config, id int) error {
	var err error
	d := document.NewDocument(cfg.GoogleConfig.SpreadSheetId, gs)
	err = d.GetDocumentSheetsListAndName()
	if err != nil {
		return err
	}

	document.GetExcelColumnName(123)

	sheetName := d.GetSheetById(id)
	start := time.Now()
	startDate, endDate, err := ExtractDatesFromSheetName(sheetName)
	if err != nil {
		err = fmt.Errorf("can not extract dates from sheet name: %w", err)
		return err
	}

	s := NewSchedule(startDate, endDate, d.SpsheetName)

	err = s.ScheduleDates.SetYear()
	if err != nil {
		return err
	}

	err = s.ScheduleDates.SetDates()
	if err != nil {
		return err
	}

	daysColumnData, err := d.GetDaysOfweek(sheetName)
	if err != nil {
		return err
	}

	err = s.ParseDatesFromSlice(daysColumnData)
	if err != nil {
		return err
	}

	s.ScheduleDates.SetWeekNum()
	ok, err := s.ValidateDates()
	if err != nil || !ok {
		return errors.New("failed validating the dates from sheetname and sheet data")
	}
	end := time.Now()

	fmt.Printf("time the schedule preparing took %v\n", end.Sub(start))

	lessonsTimingsData, err := d.GetLessonsTimings(sheetName)
	if err != nil {
		return err
	}
	err = s.ParseLessonsTimings(lessonsTimingsData)
	if err != nil {
		return err
	}

	fmt.Println(s.String())

	//data := d.GetSheduleData(latest)
	//fancy, _ := json.MarshalIndent(data, "", "    ")
	//fmt.Println(string(fancy))

	return err
}
