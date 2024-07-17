package document

import (
	"fmt"
	"google.golang.org/api/sheets/v4"
	"log"
	"strings"
)

const (
	daysOfWeekRange     string = "A1:A100"
	lessonsTimingsRange string = "B%d:B100"
	scheduleDataRange   string = "A%d:ZZ100"
)

type Document struct {
	Id           string
	srv          *sheets.Service
	DataColumnId int
}

func NewDocument(id string, srv *sheets.Service) Document {
	return Document{
		Id:  id,
		srv: srv,
	}
}

func (d *Document) GetSheetsList() []*sheets.Sheet {
	shSheetInfo, err := d.srv.Spreadsheets.Get(d.Id).Do()
	if err != nil {
		log.Fatalf("fucked up to read a spreadsheet %v", err)
	}
	sheetsList := shSheetInfo.Sheets

	return sheetsList
}

func (d *Document) GetLatestSheet() string {
	sheetsList := d.GetSheetsList()
	lastSheet := sheetsList[len(sheetsList)-1]

	return lastSheet.Properties.Title
}

func (d *Document) GetSheetData(sheetName, cellsRange string) [][]interface{} {
	readRange := fmt.Sprintf("%s!%s", sheetName, cellsRange)
	fmt.Println(readRange)
	data, err := d.srv.Spreadsheets.Values.Get(d.Id, readRange).Do()
	if err != nil {
		log.Fatalf("Unable to read sheet data from sheet %s, range: %s", sheetName, cellsRange)
	}
	return data.Values
}

func (d *Document) GetDaysOfweek(sheetName string) (data [][]interface{}) {
	data = d.GetSheetData(sheetName, daysOfWeekRange)
	for i, row := range data {
		if len(row) > 0 {
			rowVal := row[0].(string)
			if strings.Contains(rowVal, "ДНИ") {
				d.DataColumnId = i
			}
		}

	}
	return data[d.DataColumnId:]
}

func (d *Document) GetLessonsTimings(sheetName string) (data [][]interface{}) {
	return d.GetSheetData(sheetName, fmt.Sprintf(lessonsTimingsRange, d.DataColumnId))
}

func (d *Document) GetSheduleData(sheetName string) [][]interface{} {
	return d.GetSheetData(sheetName, fmt.Sprintf(scheduleDataRange, d.DataColumnId))
}
