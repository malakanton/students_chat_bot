package parser_uploader

import (
	"context"
	"errors"
	"fmt"
	"github.com/jackc/pgx/v5"
	"log/slog"
	"schedule/internal/config"
	"schedule/internal/excel-parser/excel"
	teachers_parser "schedule/internal/excel-parser/teachers-parser"
	"schedule/internal/gglapi"
	"schedule/internal/gglapi/drive"
	"schedule/internal/gglapi/parser"
	"schedule/internal/gglapi/parser/timings"
	pt "schedule/internal/lib/parser-tools"
	"schedule/internal/repositories"
	"schedule/internal/repositories/lesson"
	"schedule/internal/uploader"
	"time"
)

const (
	scheduleFilePath     = "./tmp/curr_schedule.xlsx"
	teachersListFilePath = "./tmp/teachers_list.xlsx"
)

func NewParserUploader(cfg *config.Config, logger *slog.Logger, rep *repositories.Repositories, dp *parser.DocumentParser, gs *gglapi.GoogleApi) *ParserUploader {
	currDate := time.Now().Format(drive.DateLayout)
	pu := ParserUploader{
		Cfg:      cfg,
		Logger:   logger,
		Rep:      rep,
		Dp:       dp,
		Ed:       excel.NewExcelDocument(scheduleFilePath),
		Gs:       gs,
		LastDate: &currDate,
	}
	return &pu
}

type ParserUploader struct {
	Cfg      *config.Config
	Logger   *slog.Logger
	Rep      *repositories.Repositories
	Dp       *parser.DocumentParser
	Ed       *excel.ExcelDocument
	Gs       *gglapi.GoogleApi
	LastDate *string
}

func (pu *ParserUploader) DownloadExcelAndParseSheetsList(ctx context.Context, scheduled bool) (err error) {
	if scheduled {
		err = pu.CheckLastModificationDate()
		if err != nil {
			return err
		}
	}

	pu.Logger.Info("start parsing job")

	err = drive.DownloadFile(pu.Gs.DriveService, pu.Cfg.SpreadSheetId, scheduleFilePath)
	if err != nil {
		pu.Logger.Error(err.Error())
		return err
	}

	err = pu.Ed.ReadExcelFile()
	if err != nil {
		pu.Logger.Error("failed to read excel file", slog.String("err", err.Error()))
		return err
	}

	return
}

func (pu *ParserUploader) ParseAndUploadScheduleFromExcel(ctx context.Context, scheduled bool, id int) (err error) {

	err = pu.DownloadExcelAndParseSheetsList(ctx, scheduled)
	if err != nil {
		return err
	}

	if id == 0 {
		id, err = pu.CheckActiveSheet()
	}

	err = pu.Ed.ParseSheetData(id)
	if err != nil {
		pu.Logger.Error("failed to parse schedule data", slog.String("err", err.Error()))
		return err
	}

	err = pu.Ed.ParseLessonsData(pu.Logger)
	if err != nil {
		pu.Logger.Error("failed to parse lessons form excel", slog.String("err", err.Error()))
	}

	err = pu.UploadSchedule(ctx)

	return nil

}

// TODO: make this func return the array of struct with existing lessons and changed lessons
// include cells names perhaps?
func (pu *ParserUploader) UploadSchedule(ctx context.Context) (err error) {
	for groupId, lessons := range pu.Ed.GroupsSchedule {
		gr := pu.Ed.GroupsIdxMap[groupId]

		for _, parsedLesson := range lessons {
			fmt.Println(parsedLesson.String())

			l := lesson.NewLessonFromParsed(&parsedLesson, &gr, pu.Ed.ScheduleDates.WeekNum)

			err = l.SetTeacher(ctx, pu.Rep.Teach, &l.Teacher)
			if err != nil {
				return err
			}

			err = l.SetGroup(ctx, pu.Rep.Gr, &l.Group)
			if err != nil {
				return err
			}

			err = l.SetSubject(ctx, pu.Rep.Subj, &l.Subject)
			if err != nil {
				return err
			}
			// if lessons doesn't exist -> create a new lessons in db
			existingLesson, err := pu.Rep.Les.FindOne(ctx, l.Group.Name, l.Start)
			if err != nil {
				if errors.Is(err, pgx.ErrNoRows) {
					err := pu.Rep.Les.Create(ctx, &l)
					if err != nil {
						return err
					}
					pu.Logger.Info("new lesson uploaded", slog.String("lesson", l.String()))
					continue
				}
				return err
			}
			// if new lessons equals to an existing lessons -> pass through
			if l.Equals(&existingLesson) {
				continue
			}

		}
	}
	return nil
}

func (pu *ParserUploader) CheckActiveSheet() (id int, err error) {
	currDate := time.Now()
	for idx, sheetName := range pu.Ed.SheetsMap {
		if idx == 1 {
			continue
		}
		startDate, endDate, err := pt.ExtractDatesFromSheetName(sheetName, timings.LayoutDate)
		if err != nil {
			return 0, err
		}
		// subtract 2 days so during the week and previous weekend we parse current week.
		// we start to parse next week on Saturday
		startDate = startDate.AddDate(0, 0, -2)
		endDate = endDate.AddDate(0, 0, -2)

		if currDate.After(startDate) && currDate.Before(endDate) {
			return idx, nil
		}
		pu.Logger.Info(fmt.Sprintf("sheet [%s] is not suitable because of dates"))

	}
	return
}

func (pu *ParserUploader) CheckLastModificationDate() (err error) {
	pu.Logger.Info("scheduled job started")

	lastModifiedDate, err := drive.GetLastModifiedDate(pu.Gs.DriveService, pu.Dp.Cfg.SpreadSheetId, pu.Dp.Cfg.Settings.TimeZone)

	if err != nil {
		pu.Logger.Error("failed to get last modified date", slog.String("err", err.Error()))
		return fmt.Errorf("failed to get last modified date %s", err.Error())
	}
	if lastModifiedDate <= *pu.LastDate {
		return fmt.Errorf("the spreadsheet wasnt modified, last modification date is %s", lastModifiedDate)
	}

	pu.Logger.Info("spreadsheet was modified", slog.String("at", lastModifiedDate))

	return nil
}

func (pu *ParserUploader) ParseTeachersFromExcel(ctx context.Context, log *slog.Logger) (tp *teachers_parser.TeachersExcel, err error) {
	pu.Logger.Info("start teachers parsing job")

	err = drive.DownloadFile(pu.Gs.DriveService, pu.Cfg.Files.TeachersListFileId, teachersListFilePath)
	if err != nil {
		pu.Logger.Error(fmt.Sprintf("failed to download teachers file: %s", err.Error()))
		return tp, err
	}

	tp = teachers_parser.NewTeachersExcel(teachersListFilePath)

	err = tp.ReadExcelFile()
	if err != nil {
		pu.Logger.Error(fmt.Sprintf("failed to read teachers excel file: %s", err.Error()))
		return tp, err
	}

	err = tp.GetTeachersList()
	if err != nil {
		pu.Logger.Error(fmt.Sprintf("failed to get teachers from excel: %s", err.Error()))
		return tp, err
	}

	err = tp.ParseTeachersNames()
	if err != nil {
		pu.Logger.Error(fmt.Sprintf("failed to parse teachers name: %s", err.Error()))
		return tp, err
	}

	return tp, nil
}

func (pu *ParserUploader) UploadTeachers(ctx context.Context, log *slog.Logger, tp *teachers_parser.TeachersExcel) (err error) {
	teacherRep := pu.Rep.Teach

	for _, t := range tp.ParsedTeachersList {
		t.SetInitials()
		err = teacherRep.Create(ctx, t)
		if err != nil {
			return err
		}
	}
	return nil
}

// old stuff to parse from google sheets document via api
func (pu *ParserUploader) ParseAndUploadSchedule(scheduled bool, id int) (err error) {
	var lastModifiedDate string

	if scheduled {
		err = pu.CheckLastModificationDate()
		if err != nil {
			return err
		}
	}

	parsedSchedule, err := pu.Dp.ParseDocument(id)
	//teachersCounter := make(map[string]int)
	//for _, groupLessons := range parsedSchedule.GroupsSchedule {
	//	for _, lesson := range groupLessons {
	//
	//		teachersCounter[lesson.Teacher]++
	//	}
	//}
	//for teacher, count := range teachersCounter {
	//	fmt.Println(teacher, count)
	//}
	//
	//return nil

	if err != nil {
		pu.Logger.Error("error occured while parsing document", slog.String("err", err.Error()))
		return fmt.Errorf("error occured while parsing document: %s", err.Error())
	}

	sup := uploader.NewScheduleUploader(parsedSchedule, *pu.Rep, pu.Logger)

	err = sup.UploadSchedule(context.Background())
	if err != nil {
		pu.Logger.Error("failed to upload schedule:", err.Error())
		return fmt.Errorf("failed to upload schedule: %s", err.Error())
	}

	if scheduled {
		pu.LastDate = &lastModifiedDate
	}
	return nil
}
