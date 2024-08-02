package subject

import "context"

type Repository interface {
	Create(ctx context.Context, subject *Subject) error
	FindAll(ctx context.Context) (s []Subject, err error)
	FindOne(ctx context.Context, code string) (*Subject, error)
	Update(ctx context.Context, subject Subject) error
	Delete(ctx context.Context, id string) error
}
