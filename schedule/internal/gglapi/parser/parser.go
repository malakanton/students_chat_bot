package parser

import (
	"encoding/json"
	"fmt"
	"google.golang.org/api/sheets/v4"
	"schedule/internal/config"
	"schedule/internal/gglapi/document"
	"time"
)

func ParseDocument(gs *sheets.Service, cfg *config.Config) {
	d := document.NewDocument(cfg.GoogleConfig.SpreadSheetId, gs)

	latest := d.GetLatestSheet()

	data := d.GetSheetData(latest, "A1:A100")
	fancy, _ := json.MarshalIndent(data, "", "    ")
	fmt.Println(string(fancy))

	s := document.NewSchedule(2024, time.Now())

	daysColumn := d.GetDaysOfweek(latest)
	start := time.Now()
	s.GetDatesFromSlice(daysColumn)
	end := time.Now()
	fmt.Printf("parse data to structures %v\n", end.Sub(start))
}
