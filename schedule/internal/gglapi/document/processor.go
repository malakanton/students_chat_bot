package document

import (
	"fmt"
	"strings"
	"time"
)

type Schedule struct {
	Year      int
	StartDate time.Time
	Dates     []Day
}

func NewSchedule(year int, startDate time.Time) Schedule {
	return Schedule{
		Year:      year,
		StartDate: startDate,
	}
}

type Day struct {
	RowNum int
	Date   time.Time
	Id     int
	Even   bool
	Raw    string
}

func (d *Day) String() string {
	return fmt.Sprintf("Day(id=%d, rowNum=%d, date=%v, even=%v, raw='%s')", d.Id, d.RowNum, d.Date, d.Even, d.Raw)
}

func (d *Day) ParseRawString() {

}

func (s *Schedule) GetDatesFromSlice(data [][]interface{}) {
	for i, row := range data {
		if len(row) > 0 {
			rowS := row[0].(string)
			if rowS != "" && !strings.Contains(rowS, "ДНИ") {
				d := Day{
					RowNum: i,
					Date:   time.Now(),
					Even:   true,
					Raw:    rowS,
				}
				fmt.Println(&d)
			}
		}

	}
}
