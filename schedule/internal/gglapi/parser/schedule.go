package parser

import (
	"errors"
	"fmt"
	p "schedule/internal/lib/parser-tools"
	"strings"
	"time"
)

type Schedule struct {
	ScheduleDates  ScheduleDates
	Days           []Day
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

func (s *Schedule) AddNewLesson(group string, lesson Lesson) {
	s.GroupsSchedule[group] = append(s.GroupsSchedule[group], lesson)
}

func (s *Schedule) ValidateDates() (valid bool, err error) {
	if len(s.Days) == 0 {
		err = errors.New("no days in days array to check")
	}
	if s.ScheduleDates.StartDate == s.Days[0].Date {
		valid = true
	}
	return valid, err
}

func (s *Schedule) ParseDatesFromSlice(data [][]interface{}) (err error) {
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
					return fmt.Errorf("failed to parse date from cell A%d: %w", i, err)
				}

				err = d.SetYear(s.ScheduleDates.Year)
				if err != nil {
					return fmt.Errorf("failed to parse date from cell A%d: %w", i, err)
				}
				err = d.CheckEvenOdd()
				if err != nil {
					return fmt.Errorf("failed to parse date from cell A%d: %w", i, err)
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

func (s *Schedule) ParseLessonsTimings(data [][]interface{}) (err error) {
	firstDayIdx := s.Days[0].RowIdx
	for i, row := range data {
		if i < firstDayIdx {
			continue
		}
		rowString := row[0].(string)

		day := s.GetDayByRowIdx(i)
		lt := NewLessonTimeByFilial(rowString, i)

		err = lt.ParseRawString()
		if err != nil {
			return fmt.Errorf("failed to parse lessons timings from  cell B%d: %w", i, err)
		}
		err = day.AddLessonTimings(lt)
		if err != nil {
			return err
		}
	}
	return nil
}

func (s *Schedule) ParseScheduleData(data [][]interface{}, mergesMapping map[string]string, strtRow int) (err error) {
	var (
		lessonRawString string
		l               Lesson
	)

	groupsIdxMapping := p.MakeGroupdMapping(data[0])
	firstDayIdx := s.Days[0].RowIdx

	for i, row := range data {

		if i < firstDayIdx {
			continue
		}

		day := s.GetDayByRowIdx(i)
		dateTime := day.GetLessonTimingsByIdx(i)

		for j, cellData := range row {

			cellName := fmt.Sprintf("%s%d", p.GetExcelColumnName(j+3), i+strtRow+1)

			groupName, ok := groupsIdxMapping[j]

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

			if lessonRawString == "" {
				continue
			}

			loc, filial := p.ProcessLocCell(row[j+2].(string), day.Even)
			l = NewLesson(dateTime.GetTiming(getFilial(filial)), cellName, lessonRawString, loc, false, getFilial(filial))

			subLesson, err := l.ParseRawString()
			if err != nil {
				return err
			}
			if subLesson != (Lesson{}) {
				//fmt.Println(subLesson.String())
				s.AddNewLesson(groupName, subLesson)
			}

			s.AddNewLesson(groupName, l)
		}
	}
	return nil
}

func getFilial(f int) Filial {
	switch f {
	case 1:
		return no
	default:
		return av
	}
}
