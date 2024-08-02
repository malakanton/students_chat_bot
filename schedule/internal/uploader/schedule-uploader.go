package uploader

import (
	"context"
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

func NewScheduleUploader(sc parser.Schedule, gr group.Repository, teach teacher.Repository, les lesson.Repository, subj subject.Repository) ScheduleUploader {
	return ScheduleUploader{
		sc:    sc,
		gr:    gr,
		teach: teach,
		les:   les,
		subj:  subj,
	}
}

func (sup *ScheduleUploader) UploadSchedule(ctx context.Context) (err error) {
	for groupName, lessons := range sup.sc.GroupsSchedule {

		for _, parsedLesson := range lessons {
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

			// if lesson doesnt exist -> create a new lesson in db
			existingLesson, err := sup.les.FindOne(ctx, l.Group.Name, l.Start)
			if err != nil {
				if err.Error() == lesson.NoRows {
					err := sup.les.Create(ctx, &l)
					if err != nil {
						return err
					}
					sup.logger.Info("new lesson uploaded")
					continue
				}
				return err
			}
			// if new lesson equals to an existing lesson -> pass through
			if l.Equals(&existingLesson) {
				continue
			}

		}
	}
	return nil
}
