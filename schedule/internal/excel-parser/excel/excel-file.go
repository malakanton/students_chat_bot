package excel

import (
	"errors"
	"fmt"
	"github.com/xuri/excelize/v2"
	"log/slog"
	"regexp"
	"schedule/internal/gglapi/parser"
	"schedule/internal/gglapi/parser/timings"
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
		filePath:       filePath,
		LessonTimings:  make(map[int]*timings.LessonTimeByFilial),
		GroupsIdxMap:   make(map[int]parser.Group),
		MegresMapping:  make(map[string]string),
		GroupsSchedule: make(map[string][]parser.Lesson),
	}
}

type ExcelDocument struct {
	file                  *excelize.File
	filePath              string
	DataStartIdx          int
	GroupsNamesIdx        int
	SheetsMap             map[int]string
	SheetRows             [][]string
	ScheduleDates         *timings.ScheduleDates
	LessonTimings         map[int]*timings.LessonTimeByFilial
	GroupsIdxMap          map[int]parser.Group
	MegresMapping         map[string]string
	ExternalLessonsColIdx int
	GroupsSchedule        map[string][]parser.Lesson
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

	err = ed.MakeMergesMapping(sheetName)
	if err != nil {
		return fmt.Errorf("failed to make merges mapping: %s", err.Error())
	}

	//fmt.Println(ed.MegresMapping)

	return err
}

func (ed *ExcelDocument) ParseLessonsData(logger *slog.Logger) (err error) {
	for i, row := range ed.SheetRows {

		lessonTimings, ok := ed.LessonTimings[i]
		if !ok {
			continue
		}

		if i == 20 {
			break
		}

		for j, cell := range row {
			cellName := pt.CellName(j, i)
			if cell == "" {
				print()
				continue
			}

			group, ok := ed.GroupsIdxMap[j]
			if !ok {
				continue
			}

			lessonRawString, fullDay, err := ed.CheckCellMergesAndGetCellVal(i, j, row, cellName, lessonTimings.Even)
			if err != nil {
				return fmt.Errorf("%s: failed to check merges: %s", cellName, err.Error)
			}

			if fullDay {
				l := parser.NewFullDayLesson(lessonTimings.Av.Start, lessonRawString, cellName)
				fmt.Println(l.String())
				ed.AddNewLesson(group.Name, l)
				continue
			}

			loc, filial := ed.GetLocAndFilial(j, row, lessonTimings.Even)
			lessonTime := lessonTimings.GetTiming(filial)
			l := parser.NewLesson(lessonTime, cellName, lessonRawString, loc, false, filial)

			subLesson, err := l.ParseRawString()
			if err != nil {
				logger.Error(fmt.Sprintf("cell: %s error occured while parsing lesson ", cellName), slog.String("err", err.Error()))
				continue
			}
			if subLesson != (parser.Lesson{}) {
				fmt.Println(subLesson.String())
				ed.AddNewLesson(group.Name, subLesson)
			}

			fmt.Println(l.String())

			ed.AddNewLesson(group.Name, l)

			//TODO: stop trying extract teachers name from full day lesson
			//TODO: if full day lesson not covering all cells - stil skip
			// if no teacher found - fill wuth NO_TEACHER value

		}
	}
	return nil
}

func (ed *ExcelDocument) CheckCellMergesAndGetCellVal(i, j int, row []string, cellName string, even bool) (lessonRawString string, fullDay bool, err error) {
	onelessonMergeCell := pt.CellName(j+1, i)
	nextDayIdx := ed.NextDayIdx(i) - 1
	fullDayMergeCell := pt.CellName(j+1, nextDayIdx)

	if foundMerge, ok := ed.MegresMapping[cellName]; ok {

		switch foundMerge {
		case onelessonMergeCell:
			lessonRawString = row[j]

		case fullDayMergeCell:
			lessonRawString = row[j]
			fullDay = true
		}
	} else {
		lessonRawString = row[j+pt.BoolToInt(even)]
	}

	lessonRawString = pt.PrepareLessonString(lessonRawString)
	return
}

func (ed *ExcelDocument) AddNewLesson(groupName string, lesson parser.Lesson) {
	ed.GroupsSchedule[groupName] = append(ed.GroupsSchedule[groupName], lesson)
}

func (ed *ExcelDocument) GetLocAndFilial(colIdx int, row []string, even bool) (loc string, filial timings.Filial) {

	locIdx := colIdx + 2
	if pt.GetExcelColumnName(colIdx) == "CP" {
		locIdx = colIdx + 1
	}

	if colIdx < ed.ExternalLessonsColIdx {
		filial = timings.AV
	} else {
		filial = timings.EXT
	}

	if locIdx >= len(row) {
		loc = ""
	} else {
		loc, filial = ed.ProcessLocCell(row[locIdx], even, filial)
	}
	return loc, filial
}

func (ed *ExcelDocument) ProcessLocCell(s string, even bool, filial timings.Filial) (loc string, resFilial timings.Filial) {
	var whenDoubleIdx int
	if even {
		whenDoubleIdx = 1
	}
	resFilial = filial
	s = strings.Replace(s, "\n", " ", -1)
	switch {
	case strings.Contains(s, "с/з") || strings.Contains(s, "а/з"):
		loc = s
	case strings.Contains(s, "дист"):
		loc = "дистант"
	case strings.Contains(s, "/"):
		loc = strings.Split(s, "/")[whenDoubleIdx]
	default:
		loc = s
	}
	if strings.Contains(loc, "НО") || strings.Contains(loc, "АМ") {
		loc = strings.Trim(loc, "НО")
		loc = strings.Trim(loc, "АМ")
		resFilial = timings.NO
	}

	return strings.TrimSpace(loc), resFilial
}

func (ed *ExcelDocument) NextDayIdx(currDayIdx int) (nextDayIdx int) {
	currDate := ed.LessonTimings[currDayIdx].Av.Start
	nextDayIdx = currDayIdx

	for i := currDayIdx; i < len(ed.LessonTimings); i++ {

		if compareDates(currDate, ed.LessonTimings[i].Av.Start) {
			nextDayIdx = i
			return nextDayIdx
		}
	}
	return currDayIdx
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

func (ed *ExcelDocument) MakeMergesMapping(sheetName string) (err error) {
	merges, err := ed.file.GetMergeCells(sheetName)
	if err != nil {
		return err
	}
	for _, merge := range merges {
		cellsRange := merge[0]
		value := merge[1]
		if value == "" {
			continue
		}
		splitted := strings.Split(cellsRange, ":")
		startCell := splitted[0]
		endCell := splitted[1]
		ed.MegresMapping[startCell] = endCell
	}
	return nil
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

	for i, cell := range ed.SheetRows[ed.GroupsNamesIdx-1] {
		if strings.Contains(cell, "ЗАОЧН") {
			ed.ExternalLessonsColIdx = i
		}
	}
	if ed.ExternalLessonsColIdx == 0 {
		return errors.New("external groups timings not found")
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

	scheduleDates := timings.NewScheduleDates(startDate, endDate, header)

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
	//fmt.Println(scheduleDates.String())
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

		timings := timings.NewLessonTimeByFilial(row[2], i)
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

		err = timings.SetEvenOdd()
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
		if i == ed.ExternalLessonsColIdx {
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
		cell := pt.CellName(ed.ExternalLessonsColIdx, i)

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
			return fmt.Errorf("cell %s: %s", cell, err.Error())
		}
		lessonNum++
	}
	return nil
}

func compareDates(d1, d2 time.Time) bool {
	oneDay := 24 * time.Hour
	d1 = d1.Truncate(oneDay)
	d2 = d2.Truncate(oneDay)
	//fmt.Println(d1, d2, d1.After(d2))
	return d1.After(d2)
}
