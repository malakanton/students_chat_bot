package document

import (
	"fmt"
	"google.golang.org/api/sheets/v4"
	"strings"
)

const (
	daysOfWeekRange     string = "A1:A100"
	lessonsTimingsRange string = "C%d:C100"
	scheduleDataRange   string = "D%d:ZZ100"
	//scheduleDataRange string = "C%d:E14"
)

type Document struct {
	Id              string
	srv             *sheets.Service
	SheetsNamesList []string
	DataRowId       int // a row number where the schedule table starts (with groups list)
	SpsheetName     string
}

func NewDocument(id string, srv *sheets.Service) Document {
	d := Document{
		Id:  id,
		srv: srv,
	}
	return d
}

func (d *Document) GetDocumentSheetsListAndName() error {
	shSheetInfo, err := d.srv.Spreadsheets.Get(d.Id).Do()
	if err != nil {
		return fmt.Errorf("failed to get spreadsheet info %w", err)
	}
	sheetsList := shSheetInfo.Sheets

	for _, sheet := range sheetsList {
		d.SheetsNamesList = append(d.SheetsNamesList, sheet.Properties.Title)
	}

	d.SpsheetName = shSheetInfo.Properties.Title

	return nil
}

func (d *Document) GetSheetById(id int) string {
	switch {
	case id >= len(d.SheetsNamesList) || id == -1:
		return d.GetLatestSheet()
	case id < -1:
		return d.SheetsNamesList[len(d.SheetsNamesList)+id]
	default:
		return d.SheetsNamesList[id]
	}
}

func (d *Document) GetLatestSheet() string {
	lastSheet := d.SheetsNamesList[len(d.SheetsNamesList)-1]

	return lastSheet
}

func (d *Document) GetSheetData(sheetName, cellsRange string) ([][]interface{}, error) {
	readRange := fmt.Sprintf("%s!%s", sheetName, cellsRange)
	data, err := d.srv.Spreadsheets.Values.Get(d.Id, readRange).Do()
	if err != nil {
		err = fmt.Errorf("Unable to read sheet data from sheet %s, range: %s, error: %v", sheetName, cellsRange, err)
		return nil, err
	}

	return data.Values, nil
}

func (d *Document) GetDaysOfweek(sheetName string) (data [][]interface{}, err error) {
	data, err = d.GetSheetData(sheetName, daysOfWeekRange)
	if err != nil {
		return nil, err
	}
	for i, row := range data {
		if len(row) > 0 {
			rowVal := row[0].(string)
			if strings.Contains(rowVal, "ДНИ") {
				d.DataRowId = i + 1
			}
		}
	}
	return data[d.DataRowId:], nil
}

func (d *Document) GetLessonsTimings(sheetName string) ([][]interface{}, error) {
	return d.GetSheetData(sheetName, fmt.Sprintf(lessonsTimingsRange, d.DataRowId+1))
}

func (d *Document) GetSheduleData(sheetName string) ([][]interface{}, []*sheets.GridRange, error) {
	resp, _ := d.srv.Spreadsheets.Get(d.Id).Ranges(sheetName + "!" + fmt.Sprintf(scheduleDataRange, d.DataRowId+1)).Do()
	merges := resp.Sheets[0].Merges
	values, err := d.GetSheetData(sheetName, fmt.Sprintf(scheduleDataRange, d.DataRowId+1))
	return values, merges, err
}
