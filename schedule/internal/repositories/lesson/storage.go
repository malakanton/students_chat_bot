package lesson

import (
	"context"
	"time"
)

type Repository interface {
	Create(ctx context.Context, lesson *Lesson) error
	FindAll(ctx context.Context) (l []Lesson, err error)
	FindOne(ctx context.Context, groupName string, startTime time.Time) (Lesson, error)
	Update(ctx context.Context, lesson Lesson) error
	Delete(ctx context.Context, id string) error
}
