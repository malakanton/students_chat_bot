package parser

import (
	"fmt"
	"strings"
	"time"

	p "schedule/internal/lib/parser-tools"
)

type Filial int

const (
	ext Filial = iota
	av
	no
)

type LessonTimeByFilial struct {
	RowId     int
	RawString string
	Ext       LessonTime
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
	Start time.Time
	End   time.Time
}

func (l *LessonTimeByFilial) String() string {
	return fmt.Sprintf(
		"AV Start %s End %s NO Start %s End %s\n",
		l.Av.Start.Format("15:04:05"),
		l.Av.End.Format("15:04:05"),
		l.No.Start.Format("15:04:05"),
		l.No.End.Format("15:04:05"),
	)
}

func (l *LessonTime) AddDate(date time.Time) (err error) {
	layout := layoutFullDate + " " + layoutTime
	l.Start, err = time.Parse(layout, date.Format(layoutFullDate)+" "+l.Start.Format(layoutTime))
	if err != nil {
		return err
	}
	l.End, err = time.Parse(layout, date.Format(layoutFullDate)+" "+l.End.Format(layoutTime))
	if err != nil {
		return err
	}
	return nil
}

func (l *LessonTimeByFilial) GetTiming(filial Filial) LessonTime {
	switch filial {
	case ext:
		return l.Ext
	case av:
		return l.Av
	case no:
		return l.No
	default:
		return l.Av
	}
}

func (l *LessonTimeByFilial) ParseRawString(ext bool) (err error) {
	if !ext {
		splitted := strings.Split(l.RawString, "НО")

		if len(splitted) == 1 {
			l.Av.Start, l.Av.End, err = p.MakeTimeFromString(splitted[0])
		} else if len(splitted) == 2 {
			l.Av.Start, l.Av.End, err = p.MakeTimeFromString(splitted[0])
			l.No.Start, l.No.End, err = p.MakeTimeFromString(splitted[1])
		}
		return err
	} else {
		l.Ext.Start, l.Ext.End, err = p.MakeTimeFromString(l.RawString)
		return err
	}
}
