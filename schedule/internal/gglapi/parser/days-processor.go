package parser

import (
	"errors"
	"fmt"
	"regexp"
	p "schedule/internal/lib/parser-tools"
	"time"
)

const (
	layoutDate     string = "02.01"
	layoutFullDate        = "2006-01-02"
	layoutTime            = "15:04:05"
)

type Day struct {
	RowIdx  int
	Date    time.Time
	Id      int
	Even    bool
	raw     string
	Lessons []LessonTimeByFilial
}

func (d *Day) String() string {
	return fmt.Sprintf("Day(id=%d, rowIdx=%d, date=%s, even=%v)",
		d.Id, d.RowIdx, d.Date.Format("2006-01-02"), d.Even)
}

func (d *Day) AddLessonTimings(lessonTime LessonTimeByFilial) (err error) {
	err = lessonTime.Av.AddDate(d.Date)
	if err != nil {
		return err
	}
	err = lessonTime.No.AddDate(d.Date)
	if err != nil {
		return err
	}
	d.Lessons = append(d.Lessons, lessonTime)
	return nil
}

func (d *Day) GetLessonTimingsByIdx(idx int) *LessonTimeByFilial {
	return &d.Lessons[idx-d.RowIdx]
}

func (d *Day) ParseDatesString() error {

	re, _ := regexp.Compile(`\d{1,2}.\d{1,2}`)
	found := re.FindAllString(d.raw, -1)
	if len(found) != 1 {
		return errors.New("didnt manage to find date in week day cell")
	}

	dateParsed, err := time.Parse(layoutDate, found[0])
	if err != nil {
		return err
	}

	d.Date = dateParsed
	return nil
}

func (d *Day) SetYear(year string) (err error) {
	d.Date, err = p.CombineYearAndDate(year, layoutDate, d.Date)
	return err
}

func (d *Day) CheckEvenOdd() (err error) {
	var year int

	if d.Date.Month() >= 9 {
		year = d.Date.Year()
	} else {
		year = d.Date.Year() - 1
	}

	firstSeptember, err := time.Parse("2006-01-02", fmt.Sprintf("%d", year)+"-"+"09-01")
	if err != nil {
		return err
	}

	diff := d.Date.Sub(firstSeptember)
	diffDays := int(diff.Hours()) / 24

	if (diffDays/7+1)%2 == 0 {
		d.Even = true
	} else {
		d.Even = false
	}
	return nil
}

func (d *Day) SetId() {
	d.Id = int(d.Date.Weekday())
}
