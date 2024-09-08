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
	Av        LessonTime
	No        LessonTime
	Ext       LessonTime
}

func NewLessonTimeByFilial(s string, i int) LessonTimeByFilial {
	return LessonTimeByFilial{
		RowId:     i,
		RawString: s,
	}
}

type LessonTime struct {
	Num   int
	Start time.Time
	End   time.Time
}

func (l *LessonTimeByFilial) String() string {
	return fmt.Sprintf(
		"Date %s AV #%d Start %s End %s NO #%d Start %s End %s\n EXT #%d Start %s End %s\n",
		l.Av.Start.Format(layoutFullDate),
		l.Av.Num,
		l.Av.Start.Format(layoutTime),
		l.Av.End.Format(layoutTime),
		l.No.Num,
		l.No.Start.Format(layoutTime),
		l.No.End.Format(layoutTime),
		l.Ext.Num,
		l.Ext.Start.Format(layoutTime),
		l.Ext.End.Format(layoutTime),
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

func (l *LessonTimeByFilial) AddDateToTime(date time.Time) (err error) {
	err = l.Av.AddDate(date)
	if err != nil {
		return err
	}
	err = l.No.AddDate(date)
	if err != nil {
		return err
	}
	return nil
}

func (l *LessonTimeByFilial) AddDateToTimeExt(date time.Time) (err error) {
	err = l.Ext.AddDate(date)
	if err != nil {
		return err
	}
	return nil
}

func (l *LessonTimeByFilial) AddExternalDateFromString(s string, lessonNum int) (err error) {
	l.Ext.Start, l.Ext.End, err = p.MakeTimeFromString(s)
	if err != nil {
		return err
	}
	l.Ext.Num = lessonNum
	err = l.AddDateToTimeExt(l.Av.Start)
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

func (lt *LessonTimeByFilial) AddExtDateToTime(date time.Time) error {
	if err := lt.Ext.AddDate(date); err != nil {
		return err
	}
	return nil
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

func (l *LessonTimeByFilial) SetLessonNum(num int) {
	l.Av.Num = num
	l.No.Num = num
}
