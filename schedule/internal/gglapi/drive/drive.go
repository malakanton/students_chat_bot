package drive

import (
	"google.golang.org/api/drive/v3"
	"time"
)

const DateLayout = "2006-01-02T15:04:05.999Z"

func GetLastModifiedDate(gd *drive.Service, sheetId, timeZone string) (string, error) {
	file, err := gd.Files.Get(sheetId).Fields("modifiedTime").Do()
	if err != nil {
		return "", err
	}
	date, err := time.Parse(DateLayout, file.ModifiedTime)
	if err != nil {
		return "", err
	}
	loc, err := time.LoadLocation(timeZone)
	if err != nil {
		return "", err
	}

	return date.In(loc).Format(DateLayout), err
}
