package parser

import (
	"errors"
	"fmt"
	"regexp"
	p "schedule/internal/lib/parser-tools"
	"time"
)

type ScheduleDates struct {
	Year      string
	StartDate time.Time
	EndDate   time.Time
	WeekNum   int
	header    string
}

func (s *ScheduleDates) SetYear() error {
	if s.header == "" {
		return errors.New("spreadsheet header is empty")
	}

	re, _ := regexp.Compile(`\d{4}`)
	found := re.FindAllString(s.header, -1)
	if len(found) != 2 {
		return fmt.Errorf("no years found in header")
	}

	if s.StartDate.Month() >= 9 {
		s.Year = found[0]
	} else {
		s.Year = found[1]
	}

	return nil
}

func (s *ScheduleDates) SetDates() (err error) {
	s.StartDate, err = p.CombineYearAndDate(s.Year, layoutDate, s.StartDate)
	s.EndDate, err = p.CombineYearAndDate(s.Year, layoutDate, s.EndDate)
	return err
}

func (s *ScheduleDates) SetWeekNum() {
	_, s.WeekNum = s.StartDate.ISOWeek()
}