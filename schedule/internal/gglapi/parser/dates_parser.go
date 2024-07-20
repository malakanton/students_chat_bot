package parser

import (
	"errors"
	"fmt"
	"regexp"
	"strings"
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
	s.StartDate, err = CombineYearAndDate(s.Year, s.StartDate)
	s.EndDate, err = CombineYearAndDate(s.Year, s.EndDate)
	return err
}

func (s *ScheduleDates) SetWeekNum() {
	_, s.WeekNum = s.StartDate.ISOWeek()
}

func ExtractDatesFromSheetName(s string) (startDate, endDate time.Time, err error) {
	datesInSheetName := strings.Split(s, "-")

	if len(datesInSheetName) != 2 {
		err := errors.New("failed to parse dates from sheet name")
		return startDate, endDate, err
	}

	startDate, err = time.Parse(layoutDate, strings.Trim(datesInSheetName[0], " "))
	endDate, err = time.Parse(layoutDate, strings.Trim(datesInSheetName[1], " "))

	return startDate, endDate, err
}

func CombineYearAndDate(year string, date time.Time) (full time.Time, err error) {
	fullString := year + "." + date.Format(layoutDate)
	full, err = time.Parse("2006.02.01", fullString)
	return full, err
}
