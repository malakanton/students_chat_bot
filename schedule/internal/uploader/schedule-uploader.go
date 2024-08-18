package uploader

import (
	"context"
	"errors"
	"fmt"
	"github.com/jackc/pgx/v5"
	"log/slog"
	"schedule/internal/gglapi/parser"
	"schedule/internal/repositories/group"
	"schedule/internal/repositories/lesson"
	"schedule/internal/repositories/subject"
	"schedule/internal/repositories/teacher"
)

type ScheduleUploader struct {
	logger *slog.Logger
	sc     parser.Schedule
	gr     group.Repository
	teach  teacher.Repository
	les    lesson.Repository
	subj   subject.Repository
}

func NewScheduleUploader(sc parser.Schedule, gr group.Repository, teach teacher.Repository, les lesson.Repository, subj subject.Repository, logger *slog.Logger) ScheduleUploader {
	return ScheduleUploader{
		logger: logger,
		sc:     sc,
		gr:     gr,
		teach:  teach,
		les:    les,
		subj:   subj,
	}
}

func (sup *ScheduleUploader) UploadSchedule(ctx context.Context) (err error) {
	for groupName, lessons := range sup.sc.GroupsSchedule {

		for _, parsedLesson := range lessons {
			fmt.Println(parsedLesson.String())
			l := lesson.NewLessonFromParsed(&parsedLesson, groupName, sup.sc.ScheduleDates.WeekNum)

			err = l.SetTeacher(ctx, sup.teach, &l.Teacher)
			if err != nil {
				return err
			}

			err = l.SetGroup(ctx, sup.gr, &l.Group)
			if err != nil {
				return err
			}

			err = l.SetSubject(ctx, sup.subj, &l.Subject)
			if err != nil {
				return err
			}
			// if lessons doesn't exist -> create a new lessons in db
			existingLesson, err := sup.les.FindOne(ctx, l.Group.Name, l.Start)
			if err != nil {
				if errors.Is(err, pgx.ErrNoRows) {
					err := sup.les.Create(ctx, &l)
					if err != nil {
						return err
					}
					sup.logger.Info("new lessons uploaded", slog.String("lessons", l.String()))
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
