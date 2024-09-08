package excel

import (
	"errors"
	"fmt"
	"github.com/xuri/excelize/v2"
	"regexp"
	"schedule/internal/gglapi/parser"
	pt "schedule/internal/lib/parser-tools"
	"slices"
	"strconv"
	"strings"
	"time"
)

const (
	layoutDate     string = "02.01"
	layoutFullDate        = "2006-01-02"
	layoutTime            = "15:04:05"
	headerString          = "УЧЕБНОГО ГОДА"
)

func NewExcelDocument(filePath string) *ExcelDocument {

	return &ExcelDocument{
		filePath:      filePath,
		LessonTimings: make(map[int]*parser.LessonTimeByFilial),
		GroupsIdxMap:  make(map[int]parser.Group),
	}
}

type ExcelDocument struct {
	file                  *excelize.File
	filePath              string
	DataStartIdx          int
	GroupsNamesIdx        int
	SheetsMap             map[int]string
	SheetRows             [][]string
	ScheduleDates         *parser.ScheduleDates
	LessonTimings         map[int]*parser.LessonTimeByFilial
	GroupsIdxMap          map[int]parser.Group
	ExternalLessonsColIdx int
}

func (ed *ExcelDocument) ReadExcelFile() error {
	f, err := excelize.OpenFile(ed.filePath)
	if err != nil {
		return err
	}

	defer func() {
		if err := f.Close(); err != nil {
			fmt.Println("failed to close excel file", err.Error())
		}
	}()

	ed.file = f

	return nil
}

func (ed *ExcelDocument) ParseSheetData(id int) (err error) {
	sheetName, err := ed.GetSheetNameByIdx(id)
	fmt.Printf("working on sheet %s\n", sheetName)
	if err != nil {
		return err
	}

	startDate, endDate, err := pt.ExtractDatesFromSheetName(sheetName, layoutDate)
	if err != nil {
		err = fmt.Errorf("can not extract dates from sheet name: %w", err)
		return err
	}

	err = ed.GetRowsData(sheetName)
	if err != nil {
		err = fmt.Errorf("failed to get rows data: %w", err)
		return err
	}

	err = ed.SetScheduleDates(startDate, endDate)
	if err != nil {
		return err
	}

	err = ed.ParseLessonTimings()
	if err != nil {
		return err
	}

	err = ed.GetGroupsMapping()
	if err != nil {
		return err
	}

	err = ed.ParseExternalLessonsTimings()
	if err != nil {
		return err
	}

	fmt.Println(ed.LessonTimings)

	fmt.Println(ed.GroupsIdxMap)

	return err
}

func (ed *ExcelDocument) GetSheetsMap() {
	ed.SheetsMap = ed.file.GetSheetMap()
}

func (ed *ExcelDocument) GetSheetNameByIdx(idx int) (sheetName string, err error) {
	ed.GetSheetsMap()

	if idx >= 0 {
		if sheetName, ok := ed.SheetsMap[idx]; ok {
			return sheetName, nil
		}
		return sheetName, fmt.Errorf("sheet name with index %d doesnt exist", idx)
	}
	// if negative index passed
	sheetsList := ed.file.GetSheetList()
	latestIdx := len(sheetsList) + idx

	return sheetsList[latestIdx], err
}

func (ed *ExcelDocument) GetRowsData(sheetName string) error {
	rows, err := ed.file.GetRows(sheetName)
	if err != nil {
		return err
	}
	ed.SheetRows = rows

	err = ed.FindIndexes()

	return err
}

func (ed *ExcelDocument) FindIndexes() (err error) {
	for i, row := range ed.SheetRows {
		if len(row) < 2 {
			continue
		}
		if slices.Contains(row, "ауд.") {
			ed.GroupsNamesIdx = i
		}

		if strings.Contains(row[0], "ПОН") {
			ed.DataStartIdx = i
		}
	}
	if ed.GroupsNamesIdx == 0 {
		return errors.New("groups names index is not found")
	}
	if ed.DataStartIdx == 0 {
		return errors.New("data start index not found")
	}
	return nil
}

func (ed *ExcelDocument) SetScheduleDates(startDate, endDate time.Time) (err error) {

	var header string

	for _, row := range ed.SheetRows {
		if len(row) == 1 {
			value := row[0]
			if strings.Contains(value, headerString) {
				header = value
			}
		}
	}

	if header == "" {
		return errors.New("didnt manage to find schedule header to parse year")
	}

	scheduleDates := parser.NewScheduleDates(startDate, endDate, header)

	err = scheduleDates.SetYear()
	if err != nil {
		return err
	}

	err = scheduleDates.SetDates()
	if err != nil {
		return err
	}

	scheduleDates.SetWeekNum()

	ed.ScheduleDates = scheduleDates
	fmt.Println(scheduleDates.String())
	return nil
}

func (ed *ExcelDocument) ParseLessonTimings() (err error) {
	var (
		currDate  = ed.ScheduleDates.StartDate
		lessonNum int
	)
	for i, row := range ed.SheetRows {
		if i < ed.DataStartIdx {
			continue
		}

		if row[0] != "" {
			newDate, err := pt.ExtractDateFromString(row[0], layoutDate, ed.ScheduleDates.Year)

			if err != nil && lessonNum == 1 {
				currDate = currDate.AddDate(0, 0, 1)

			} else {
				currDate = newDate
			}
		}

		lessonNum, err = strconv.Atoi(row[1])
		if err != nil {
			lessonNum++
		}

		timings := parser.NewLessonTimeByFilial(row[2], i)
		err = timings.ParseRawString(false)
		if err != nil {
			cellName := pt.CellName(2, i)
			//return fmt.Errorf("cell: %s error: %s", cellName, err.Error())
			fmt.Printf("cell: %s error: %s\n", cellName, err.Error())
		}

		timings.SetLessonNum(lessonNum)
		err = timings.AddDateToTime(currDate)
		if err != nil {
			return err
		}

		ed.LessonTimings[i] = &timings
	}
	return nil
}

func (ed *ExcelDocument) GetGroupsMapping() error {
	re := regexp.MustCompile(`[А-Я]{1,4}\d{1,2}-\d{1,3}[а-яА-Я]+`)
	groupsRow := ed.SheetRows[ed.GroupsNamesIdx]
	studyForm := parser.In

	for i, cell := range groupsRow {
		if strings.Contains(cell, "ЗАОЧНО") {
			ed.ExternalLessonsColIdx = i
			studyForm = parser.Ex
		}

		foundGroupName := re.FindString(cell)
		if foundGroupName == "" {
			continue
		}

		g := parser.NewGroup(foundGroupName, studyForm)

		ed.GroupsIdxMap[i] = g
	}
	if len(ed.GroupsIdxMap) < 20 {
		return errors.New("not all groups are found")
	}

	return nil
}

func (ed *ExcelDocument) ParseExternalLessonsTimings() (err error) {

	lessonNum := 1
	currDate := ed.ScheduleDates.StartDate
	for i, row := range ed.SheetRows {
		if i < ed.DataStartIdx || ed.ExternalLessonsColIdx >= len(row) {
			continue
		}

		externalLessonTimeCell := row[ed.ExternalLessonsColIdx]

		if externalLessonTimeCell == "" {
			continue
		}
		l := ed.LessonTimings[i]

		if compareDates(l.Av.Start, currDate) {
			currDate = currDate.AddDate(0, 0, 1)
			lessonNum = 1
		}

		err = l.AddExternalDateFromString(externalLessonTimeCell, lessonNum)
		if err != nil {
			return err
		}
		lessonNum++
	}
	return nil
}

func compareDates(d1, d2 time.Time) bool {
	oneDay := 24 * time.Hour
	d1 = d1.Truncate(oneDay)
	d2 = d2.Truncate(oneDay)
	fmt.Println(d1, d2, d1.After(d2))
	return d1.After(d2)
}
