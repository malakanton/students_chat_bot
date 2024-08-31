package parser

import (
	"fmt"
	"regexp"
	p "schedule/internal/lib/parser-tools"
	"strings"
	"time"
)

var BadWords = []string{"инейка", "САМОСТОЯТЕЛЬНОЙ"}

type Schedule struct {
	ScheduleDates  ScheduleDates
	Days           []Day
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
		ScheduleDates: ScheduleDates{
			StartDate: startDate,
			EndDate:   endDate,
			header:    header,
		},
		Days:           []Day{},
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
				d := Day{
					RowIdx: i,
					Even:   true,
					raw:    rowS,
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

func (s *Schedule) GetDayByRowIdx(idx int) *Day {
	var neededDay *Day
	for i, day := range s.Days {
		if idx >= day.RowIdx {
			neededDay = &s.Days[i]
		} else {
			return neededDay
		}
	}
	return neededDay
}

func (s *Schedule) GetNextDayRowIdx(currDay *Day, dataLength int) int {
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
		if !externalTimings {
			lt := NewLessonTimeByFilial(rowString, i)
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
			err = lt.ParseRawString(externalTimings)
			if err != nil {
				return fmt.Errorf("%s failed to parse external lesson timings from cell %s%d: %w", op, cellPrefix, i, err)
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

	err = s.ParseLessonsTimings(data, extFormTimingsIdx)
	if err != nil {
		return fmt.Errorf("%s %w", op, err)
	}

	s.SetGroups(groupsIdxMapping)

	firstDayIdx := s.Days[0].RowIdx

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
				wholeDay := NewFullDayLesson(day, p.PrepareLessonString(cellData), cellName)
				//fmt.Println(wholeDay.String())
				s.AddNewLesson(groupName, wholeDay)
				continue

			default:
				lessonRawString = p.PrepareLessonString(row[j+p.BoolToInt(day.Even)])
			}

			if notValidLesson(lessonRawString) {
				continue
			}

			var (
				loc    string
				filial int
			)
			if maxIdx := len(row) - 1; maxIdx >= j+2 {
				locIdx := j + 2
				val := row[locIdx].(string)
				if len([]rune(val)) > 10 {
					val = row[locIdx-1].(string)
				}
				loc, filial = p.ProcessLocCell(val, day.Even)
			} else {
				loc, filial = "", 1
			}

			if group.StudyForm == Ex {
				filial = 0
			}

			l = NewLesson(dateTime.GetTiming(getFilial(filial)), cellName, lessonRawString, loc, false, getFilial(filial))

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

func getFilial(f int) Filial {
	switch f {
	case 0:
		return ext
	case 1:
		return no
	default:
		return av
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
