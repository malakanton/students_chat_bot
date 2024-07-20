package parser

import (
	"errors"
	"fmt"
	"strings"
	"time"
)

type Schedule struct {
	ScheduleDates ScheduleDates
	Days          []Day
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

func NewSchedule(startDate, endDate time.Time, header string) Schedule {
	s := Schedule{
		ScheduleDates: ScheduleDates{
			StartDate: startDate,
			EndDate:   endDate,
			header:    header,
		},
		Days: []Day{},
	}
	return s
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

func (s *Schedule) ParseLessonsTimings(data [][]interface{}) (err error) {
	var dayIdx = 0

	for i, row := range data {
		if len(row) == 0 || i < s.Days[0].RowIdx {
			continue
		}
		rowString := row[0].(string)

		if dayIdx+1 < len(s.Days) {
			if nextDayIdx := s.Days[dayIdx+1].RowIdx; i >= nextDayIdx {
				dayIdx++
			}
		}

		l := LessonTimeByFilial{
			RawString: rowString,
		}
		err = l.ParseRawString()
		if err != nil {
			return fmt.Errorf("failed to parse lesson timings from  cell B%d: %w", i, err)
		}
		s.Days[dayIdx].Lessons = append(s.Days[dayIdx].Lessons, l)

	}
	return nil
}
