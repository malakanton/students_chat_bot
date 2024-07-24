package parser

import (
	"errors"
	"fmt"
	"google.golang.org/api/sheets/v4"
	"schedule/internal/config"
	"schedule/internal/gglapi/document"
	"time"
)

func ParseDocument(gs *sheets.Service, cfg *config.Config, id int) (err error) {
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

	lessonsTimingsData, err := d.GetLessonsTimings(sheetName)
	if err != nil {
		return err
	}
	err = s.ParseLessonsTimings(lessonsTimingsData)
	if err != nil {
		return err
	}

	end := time.Now()
	fmt.Printf("time the schedule preparing took %v\n", end.Sub(start))

	scheduleData, merges, err := d.GetSheduleData(sheetName)
	if err != nil {
		return nil
	}

	mergesMapping := MakeMergesMapping(merges, int64(d.DataRowId), 2)
	//printOutJson(merges)

	err = s.ParseScheduleData(scheduleData, mergesMapping)
	if err != nil {
		return err
	}

	group := "ОИБ9-222Б"
	fmt.Printf("group %s\n", group)
	groupSch, ok := s.GroupsSchedule[group]
	if ok {
		for _, lesson := range groupSch {
			fmt.Println(lesson.String())
		}
	}

	return err
}

//func printOutJson(i interface{}) {
//	jsn, _ := json.MarshalIndent(i, "", "    ")
//	fmt.Println(string(jsn))
//}
