package parser_tools

import (
	"errors"
	"fmt"
	"regexp"
	"strings"
	"time"
)

func ExtractDatesFromSheetName(s, layout string) (startDate, endDate time.Time, err error) {
	const op = "lib:parser-tools:dates"
	re := regexp.MustCompile(`\d{1,2}\.\d{2}-\d{1,2}\.\d{2}`)
	founDatesdString := re.FindAllString(s, -1)
	if len(founDatesdString) != 1 {
		err = errors.New(fmt.Sprintf("%s: no dates founs in spreadsheet name", op))
		return startDate, endDate, err
	}

	datesInSheetName := strings.Split(founDatesdString[0], "-")

	if len(datesInSheetName) != 2 {
		err := errors.New(fmt.Sprintf("%s: must be two dates in sheet name, found %d", op, len(datesInSheetName)))
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
