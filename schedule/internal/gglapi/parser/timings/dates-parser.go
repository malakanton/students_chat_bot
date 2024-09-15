package timings

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
	Header    string
}

func NewScheduleDates(start, end time.Time, header string) *ScheduleDates {
	return &ScheduleDates{
		StartDate: start,
		EndDate:   end,
		Header:    header,
	}
}

func (s *ScheduleDates) SetYear() error {
	if s.Header == "" {
		return errors.New("spreadsheet header is empty")
	}

	re, _ := regexp.Compile(`\d{4}`)
	found := re.FindAllString(s.Header, -1)
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
	s.StartDate, err = p.CombineYearAndDate(s.Year, LayoutDate, s.StartDate)
	s.EndDate, err = p.CombineYearAndDate(s.Year, LayoutDate, s.EndDate)
	return err
}

func (s *ScheduleDates) SetWeekNum() {
	_, s.WeekNum = s.StartDate.ISOWeek()
}

func (s *ScheduleDates) String() string {
	return fmt.Sprintf(
		"Schedule dates: Year=%s StartDate=%s EndDate=%s WeekNum=%d",
		s.Year,
		s.StartDate.Format(LayoutDate),
		s.EndDate.Format(LayoutDate),
		s.WeekNum,
	)
}
