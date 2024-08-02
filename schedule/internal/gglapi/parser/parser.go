package parser

import (
	"errors"
	"fmt"
	"google.golang.org/api/sheets/v4"
	"schedule/internal/config"
	"schedule/internal/gglapi/document"
	pt "schedule/internal/lib/parser-tools"
)

func ParseDocument(gs *sheets.Service, cfg *config.Config, id int) (s Schedule, err error) {
	d := document.NewDocument(cfg.GoogleConfig.SpreadSheetId, gs)
	err = d.GetDocumentSheetsListAndName()
	if err != nil {
		return Schedule{}, err
	}

	sheetName := d.GetSheetById(id)

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
	err = s.ParseLessonsTimings(lessonsTimingsData)
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

	group := "ССА9-222В"
	fmt.Printf("group %s\n", group)
	groupSch, ok := s.GroupsSchedule[group]
	if ok {
		for _, lesson := range groupSch {
			fmt.Println(lesson.String())
		}
	}

	return s, nil
}

//func printOutJson(i interface{}) {
//	jsn, _ := json.MarshalIndent(i, "", "    ")
//	fmt.Println(string(jsn))
//}
