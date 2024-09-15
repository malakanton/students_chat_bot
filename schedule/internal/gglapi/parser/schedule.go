package parser

import (
	"fmt"
	"regexp"
	"schedule/internal/gglapi/parser/timings"
	p "schedule/internal/lib/parser-tools"
	"strings"
	"time"
)

var BadWords = []string{"инейка", "САМОСТОЯТЕЛЬНОЙ"}

type Schedule struct {
	ScheduleDates  timings.ScheduleDates
	Days           []timings.Day
	Groups         []Group
	GroupsSchedule map[string][]Lesson
}

func (s *Schedule) String() string {
	dateFormat := "2006-01-02"
	text := fmt.Sprintf(
		"schedule dates: from %s to %s, days:\n",
		s.ScheduleDates.StartDate.Format(dateFormat),
		s.ScheduleDates.EndDate.Format(dateFormat),
	)
	for i, d := range s.Days {
		text += fmt.Sprintf("day %d value: %v\n", i, d.String())
		for _, l := range d.Lessons {
			text += l.String()
		}
	}

	return text
}

func (s *Schedule) CountGroupsLessons() (int, int) {
	var lessonsCnt, groupsCnt int
	for _, lessons := range s.GroupsSchedule {
		groupsCnt++
		lessonsCnt += len(lessons)
	}
	return groupsCnt, lessonsCnt
}

func NewSchedule(startDate, endDate time.Time, header string) Schedule {
	s := Schedule{
		ScheduleDates: timings.ScheduleDates{
			StartDate: startDate,
			EndDate:   endDate,
			Header:    header,
		},
		Days:           []timings.Day{},
		GroupsSchedule: make(map[string][]Lesson),
	}
	return s
}

func (s *Schedule) AddNewLesson(groupName string, lesson Lesson) {
	s.GroupsSchedule[groupName] = append(s.GroupsSchedule[groupName], lesson)
}

func (s *Schedule) ValidateDates() (valid bool, err error) {
	const op = "gglapi:parser:schedule"
	if len(s.Days) == 0 {
		err = fmt.Errorf("%s: no days in days array to check", op)
	}
	if s.ScheduleDates.StartDate == s.Days[0].Date {
		valid = true
	}
	return valid, err
}

func (s *Schedule) ParseDatesFromSlice(data [][]interface{}) (err error) {
	const op = "gglapi:parser:schedule"
	currDate := s.ScheduleDates.StartDate

	for i, row := range data {

		if len(row) > 0 {
			rowS := row[0].(string)

			if rowS != "" && !strings.Contains(rowS, "ДНИ") {
				d := timings.Day{
					RowIdx: i,
					Even:   true,
					Raw:    rowS,
				}
				err = d.ParseDatesString()
				if err != nil {
					//return fmt.Errorf("%s: failed to parse date from cell A%d: %w", op, i, err)
					d.SetDate(currDate)
					currDate = currDate.AddDate(0, 0, 1)
				}

				err = d.SetYear(s.ScheduleDates.Year)
				if err != nil {
					return fmt.Errorf("%s: failed to parse date from cell A%d: %w", op, i, err)
				}
				err = d.CheckEvenOdd()
				if err != nil {
					return fmt.Errorf("%s: failed to parse date from cell A%d: %w", op, i, err)
				}

				d.SetId()
				s.Days = append(s.Days, d)
			}
		}
	}
	return nil
}

func (s *Schedule) GetDayByRowIdx(idx int) *timings.Day {
	var neededDay *timings.Day
	for i, day := range s.Days {
		if idx >= day.RowIdx {
			neededDay = &s.Days[i]
		} else {
			return neededDay
		}
	}
	return neededDay
}

func (s *Schedule) GetNextDayRowIdx(currDay *timings.Day, dataLength int) int {
	for i, day := range s.Days {
		if currDay.RowIdx == day.RowIdx {
			if i == len(s.Days)-1 {
				return dataLength
			}
			return s.Days[i+1].RowIdx
		}
	}
	return dataLength
}

func (s *Schedule) ParseLessonsTimings(data [][]interface{}, idx int) (err error) {
	const op = "gglapi:parser:schedule"
	cellPrefix := p.GetExcelColumnName(idx + 1)
	firstDayIdx := s.Days[0].RowIdx
	var externalTimings = idx != 0

	for i, row := range data {
		if i < firstDayIdx || len(row) < idx+1 {
			continue
		}

		rowString := row[idx].(string)
		if rowString == "" {
			continue
		}

		day := s.GetDayByRowIdx(i)
		fmt.Println(day.String())
		if !externalTimings {
			lt := timings.NewLessonTimeByFilial(rowString, i)
			err = lt.ParseRawString(externalTimings)

			if err != nil {
				return fmt.Errorf("%s failed to parse lessons timings from  cell %s%d: %w", op, cellPrefix, i, err)
			}

			err = day.AddLessonTimings(lt)
			if err != nil {
				return err
			}

		} else {
			lt := day.GetLessonTimingsByIdx(i)
			lt.RawString = rowString
			err = lt.ParseRawString(externalTimings)
			if err != nil {
				return fmt.Errorf("%s failed to parse external lesson timings from cell %s%d: %w", op, cellPrefix, i, err)
			}
			err = lt.AddExtDateToTime(day.Date)
			if err != nil {
				return err
			}
		}

	}
	return nil
}

func (s *Schedule) ParseScheduleData(data [][]interface{}, mergesMapping map[string]string, strtRow int) (err error) {
	const op = "gglapi:parser:parseschdata"
	var (
		lessonRawString string
		l               Lesson
	)

	groupsIdxMapping, extFormTimingsIdx := MakeGroupsMapping(data[0])
	fmt.Printf("external timings col number %d\n", extFormTimingsIdx)
	err = s.ParseLessonsTimings(data, extFormTimingsIdx)
	if err != nil {
		return fmt.Errorf("%s %w", op, err)
	}

	s.SetGroups(groupsIdxMapping)

	firstDayIdx := s.Days[0].RowIdx

	//for _, day := range s.Days {
	//	fmt.Println(day.String())
	//	for _, l := range day.Lessons {
	//		fmt.Println(l.String())
	//	}
	//}
	//return

	for i, row := range data {

		if i < firstDayIdx {
			continue
		}

		day := s.GetDayByRowIdx(i)
		dateTime := day.GetLessonTimingsByIdx(i)

		for j, cellData := range row {

			cellName := fmt.Sprintf("%s%d", p.GetExcelColumnName(j+4), i+strtRow+1)

			group, ok := groupsIdxMapping[j]
			groupName := group.Name
			if !ok {
				continue
			}

			nextDayIdx := s.GetNextDayRowIdx(day, len(data))

			cellCoord, oneLessonMerged, wholeDayMerged := p.MergedCellsRanges(i, j, nextDayIdx)
			endMerge, _ := mergesMapping[cellCoord]

			switch endMerge {

			case oneLessonMerged:
				lessonRawString = p.PrepareLessonString(cellData)

			case wholeDayMerged:
				wholeDay := NewFullDayLesson(day.Date, p.PrepareLessonString(cellData), cellName)
				//fmt.Println(wholeDay.String())
				s.AddNewLesson(groupName, wholeDay)
				continue

			default:
				lessonRawString = p.PrepareLessonString(row[j+p.BoolToInt(day.Even)])
			}

			if notValidLesson(lessonRawString) {
				continue
			}

			loc, filial := GetLocAndFilial(j, row, day)

			if group.StudyForm == Ex {
				filial = 0
			}

			l = NewLesson(dateTime.GetTiming(filial), cellName, lessonRawString, loc, false, filial)

			subLesson, err := l.ParseRawString()
			if err != nil {
				fmt.Println(err.Error())
				continue
				//return err
			}
			if subLesson != (Lesson{}) {
				//fmt.Println(subLesson.String())
				s.AddNewLesson(groupName, subLesson)
			}

			fmt.Println(l.String())

			s.AddNewLesson(groupName, l)
		}
	}
	return nil
}

func (s *Schedule) SetGroups(groups map[int]Group) {
	for _, group := range groups {
		s.Groups = append(s.Groups, group)
	}
}

func (s *Schedule) GetGroupByName(groupName string) *Group {
	for _, gr := range s.Groups {
		if gr.Name == groupName {
			return &gr
		}
	}
	return &Group{}
}

func GetLocAndFilial(colIdx int, row []interface{}, day *timings.Day) (loc string, filial timings.Filial) {
	filial = timings.AV
	locIdx := colIdx + 2
	if p.GetExcelColumnName(colIdx+4) == "CP" {
		locIdx = colIdx + 1
	}

	if locIdx >= len(row) {
		loc, filial = "", 1
	} else {
		loc, filial = ProcessLocCell(row[locIdx].(string), day.Even, filial)
	}
	return loc, filial
}

func ProcessLocCell(s string, even bool, filial timings.Filial) (loc string, resFilial timings.Filial) {
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
		resFilial = 2
	}

	return strings.TrimSpace(loc), resFilial
}

func getFilial(f int) timings.Filial {
	switch f {
	case 0:
		return timings.EXT
	case 2:
		return timings.NO
	default:
		return timings.AV
	}
}

func notValidLesson(lessonString string) bool {

	if lessonString == "" {
		return true
	}
	for _, badWord := range BadWords {
		re := regexp.MustCompile(`(?i)` + badWord)
		if found := re.FindAllString(lessonString, -1); len(found) > 0 {
			return true
		}
	}
	return false

}
