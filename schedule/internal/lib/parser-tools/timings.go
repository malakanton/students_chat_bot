package parser_tools

import (
	"fmt"
	"regexp"
	"strings"
	"time"
)

func MakeTimeFromString(s string) (strt, end time.Time, err error) {
	reTimes, _ := regexp.Compile(`\d{1,2}\.\d{1,2}-\d{1,2}\.\d{1,2}`)
	timePeriods := reTimes.FindAllString(s, -1)
	switch len(timePeriods) {
	case 0:
		err = fmt.Errorf("no time found in string %s", s)
		return strt, end, err
	case 1:
		times := strings.Split(timePeriods[0], "-")
		strt = ParseTimeString(times[0])
		end = ParseTimeString(times[1])
		return strt, end, nil
	case 2:
		strt = ParseTimeString(strings.Split(timePeriods[0], "-")[0])
		end = ParseTimeString(strings.Split(timePeriods[1], "-")[1])
		return strt, end, nil
	default:
		return strt, end, fmt.Errorf("too many dates found in string %s", s)
	}
}

func ParseTimeString(s string) time.Time {
	layout := "15.04"
	t, _ := time.Parse(layout, s)
	return t
}
