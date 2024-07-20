package parser

import (
	"fmt"
	"regexp"
	"strings"
	"time"
)

type Filial int

const (
	av Filial = iota
	no
)

type LessonTimeByFilial struct {
	RawString string
	Av        LessonTime
	No        LessonTime
}

type LessonTime struct {
	start time.Time
	end   time.Time
}

func (l *LessonTimeByFilial) GetTiming(filial Filial) LessonTime {
	switch filial {
	case av:
		return l.Av
	case no:
		return l.No
	default:
		return l.Av
	}
}

func (l *LessonTimeByFilial) ParseRawString() (err error) {

	splitted := strings.Split(l.RawString, "НО")

	if len(splitted) == 1 {
		l.Av.start, l.Av.end, err = MakeTimeFromString(splitted[0])
	} else if len(splitted) == 2 {
		l.Av.start, l.Av.end, err = MakeTimeFromString(splitted[0])
		l.No.start, l.No.end, err = MakeTimeFromString(splitted[1])
	}
	return err
}

func MakeTimeFromString(s string) (strt, end time.Time, err error) {
	reTimes, _ := regexp.Compile(`\d{1,2}\.\d{1,2}-\d{1,2}\.\d{1,2}`)
	timePeriods := reTimes.FindAllString(s, -1)
	switch len(timePeriods) {
	case 0:
		err = fmt.Errorf("No date string found in string %s", s)
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

func (l *LessonTimeByFilial) String() string {
	return fmt.Sprintf(
		"AV start %s end %s NO start %s end %s\n",
		l.Av.start.Format("15:04:05"),
		l.Av.end.Format("15:04:05"),
		l.No.start.Format("15:04:05"),
		l.No.end.Format("15:04:05"),
	)
}
