package parser

import (
	"fmt"
	"strings"
	"time"

	p "schedule/internal/lib/parser-tools"
)

type Filial int

const (
	av Filial = iota
	no
)

type LessonTimeByFilial struct {
	RowId     int
	RawString string
	Av        LessonTime
	No        LessonTime
}

func NewLessonTimeByFilial(s string, i int) LessonTimeByFilial {
	return LessonTimeByFilial{
		RowId:     i,
		RawString: s,
	}
}

type LessonTime struct {
	start time.Time
	end   time.Time
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

func (l *LessonTime) AddDate(date time.Time) (err error) {
	layout := layoutFullDate + " " + layoutTime
	l.start, err = time.Parse(layout, date.Format(layoutFullDate)+" "+l.start.Format(layoutTime))
	if err != nil {
		return err
	}
	l.end, err = time.Parse(layout, date.Format(layoutFullDate)+" "+l.end.Format(layoutTime))
	if err != nil {
		return err
	}
	return nil
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
		l.Av.start, l.Av.end, err = p.MakeTimeFromString(splitted[0])
	} else if len(splitted) == 2 {
		l.Av.start, l.Av.end, err = p.MakeTimeFromString(splitted[0])
		l.No.start, l.No.end, err = p.MakeTimeFromString(splitted[1])
	}
	return err
}
