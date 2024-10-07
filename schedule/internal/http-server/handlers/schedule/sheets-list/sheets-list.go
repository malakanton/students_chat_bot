package sheets_list

import (
	"context"
	"github.com/go-chi/render"
	"net/http"
	"schedule/internal/gglapi/drive"
	resp "schedule/internal/lib/api/response"
	pupl "schedule/internal/parser-uploader"
	"sort"
	"strings"
)

type Response struct {
	resp.Response
	LastModified     string        `json:"last_modified"`
	SpreadsheetsList []SpreadSheet `json:"spreadsheets_list,omitempty"`
}

type SpreadSheet struct {
	Id   int    `json:"id"`
	Name string `json:"name"`
}

func NewSpreadSheet(id int, name string) SpreadSheet {
	return SpreadSheet{
		Id:   id,
		Name: name,
	}
}

func GetSheetsList(ctx context.Context, pu *pupl.ParserUploader) http.HandlerFunc {
	return func(w http.ResponseWriter, r *http.Request) {

		var err error

		err = pu.DownloadExcelAndParseSheetsList(ctx, false)
		if err != nil {
			render.JSON(w, r, resp.Error(err.Error()))
			return
		}

		var m []SpreadSheet
		for idx, spName := range pu.Ed.SheetsMap {
			m = append(m, NewSpreadSheet(idx, strings.TrimSpace(spName)))
		}

		sort.Slice(m, func(i, j int) bool {
			return m[i].Id < m[j].Id
		})

		lastModifiedDate, err := drive.GetLastModifiedDate(pu.Gs.DriveService, pu.Dp.Cfg.SpreadSheetId, pu.Dp.Cfg.Settings.TimeZone)
		if err != nil {
			render.JSON(w, r, resp.Error(err.Error()))
			return
		}

		responseOK(w, r, m, lastModifiedDate)
	}
}

func responseOK(w http.ResponseWriter, r *http.Request, m []SpreadSheet, lastModified string) {
	render.JSON(w, r, Response{
		Response:         resp.OK(),
		SpreadsheetsList: m,
		LastModified:     lastModified,
	})
}
