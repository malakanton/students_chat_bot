package drive

import (
	"fmt"
	"google.golang.org/api/drive/v3"
	"io"
	"os"
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

func DownloadFile(service *drive.Service, fileID, filePath string) error {
	resp, err := service.Files.Get(fileID).Download()
	if err != nil {
		return err
	}
	defer resp.Body.Close()

	if _, err := os.Stat("tmp"); err != nil {
		if os.IsNotExist(err) {
			err = os.Mkdir("tmp", 0750)
		} else {
			return err
		}
	}

	out, err := os.Create(filePath)
	if err != nil {
		return err
	}
	defer out.Close()

	_, err = io.Copy(out, resp.Body)
	if err != nil {
		return err
	}
	fmt.Printf("downloaded file %s\n", filePath)

	return nil
}
