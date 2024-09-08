package parser_tools

import (
	"errors"
	"fmt"
	"regexp"
	"strconv"
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

func ExtractDateFromString(s, layout string, year string) (date time.Time, err error) {
	re := regexp.MustCompile(`\d{1,2}\.\d{2}`)
	found := re.FindAllString(s, -1)
	if len(found) == 0 {
		return time.Now(), fmt.Errorf("no date in string %s", s)
	}

	date, err = time.Parse(layout, strings.Trim(found[0], " "))
	yearInt, _ := strconv.Atoi(year)

	date = date.AddDate(yearInt, 0, 0)

	return date, err
}
