package parser_tools

import (
	"errors"
	"strings"
	"time"
)

func ExtractDatesFromSheetName(s, layout string) (startDate, endDate time.Time, err error) {
	datesInSheetName := strings.Split(s, "-")

	if len(datesInSheetName) != 2 {
		err := errors.New("failed to parse dates from sheet name")
		return startDate, endDate, err
	}

	startDate, err = time.Parse(layout, strings.Trim(datesInSheetName[0], " "))
	endDate, err = time.Parse(layout, strings.Trim(datesInSheetName[1], " "))

	return startDate, endDate, err
}

func CombineYearAndDate(year, layout string, date time.Time) (full time.Time, err error) {
	fullString := year + "." + date.Format(layout)
	full, err = time.Parse("2006.02.01", fullString)
	return full, err
}
