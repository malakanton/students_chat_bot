package lesson

import (
	"context"
	"time"
)

type Repository interface {
	Create(ctx context.Context, lesson *Lesson) error
	FindAll(ctx context.Context) (l []Lesson, err error)
	FindOne(ctx context.Context, groupName string, startTime time.Time) (Lesson, error)
	Update(ctx context.Context, lesson, existingLesson Lesson) error
	Delete(ctx context.Context, id string) error
	FindWeeklyForTeacher(ctx context.Context, id, weekNum int) (lessons []TeacherLessonDto, err error)
	FindDailyForTeacher(ctx context.Context, id int, date string) (lessons []TeacherLessonDto, err error)
	FindGroupWeeklySchedule(ctx context.Context, id, weekNum int) (lessons []GroupLessonDto, err error)
	FindGroupDailySchedule(ctx context.Context, id int, date string) (lessons []GroupLessonDto, err error)
}
