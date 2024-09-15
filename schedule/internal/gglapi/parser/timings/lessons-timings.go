package timings

import (
	"fmt"
	"strings"
	"time"

	p "schedule/internal/lib/parser-tools"
)

type Filial int

const (
	EXT Filial = iota
	AV
	NO
)

type LessonTimeByFilial struct {
	RowId     int
	RawString string
	Even      bool
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
		l.Av.Start.Format(LayoutFullDate),
		l.Av.Num,
		l.Av.Start.Format(LayoutTime),
		l.Av.End.Format(LayoutTime),
		l.No.Num,
		l.No.Start.Format(LayoutTime),
		l.No.End.Format(LayoutTime),
		l.Ext.Num,
		l.Ext.Start.Format(LayoutTime),
		l.Ext.End.Format(LayoutTime),
	)
}

func (l *LessonTime) AddDate(date time.Time) (err error) {
	layout := LayoutFullDate + " " + LayoutTime
	l.Start, err = time.Parse(layout, date.Format(LayoutFullDate)+" "+l.Start.Format(LayoutTime))
	if err != nil {
		return err
	}
	l.End, err = time.Parse(layout, date.Format(LayoutFullDate)+" "+l.End.Format(LayoutTime))
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
	case EXT:
		return l.Ext
	case AV:
		return l.Av
	case NO:
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

func (l *LessonTimeByFilial) SetEvenOdd() error {
	var year int
	date := l.Av.Start

	if date.Month() >= 9 {
		year = date.Year()
	} else {
		year = date.Year() - 1
	}

	firstSeptember, err := time.Parse("2006-01-02", fmt.Sprintf("%d", year)+"-"+"09-01")
	if err != nil {
		return err
	}

	diff := date.Sub(firstSeptember)
	diffDays := int(diff.Hours()) / 24

	if (diffDays/7+1)%2 == 0 {
		l.Even = true
	} else {
		l.Even = false
	}
	return nil
}
