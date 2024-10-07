package teacher

import "context"

type Repository interface {
	Create(ctx context.Context, teacher *Teacher) error
	FindAll(ctx context.Context) (t []Teacher, err error)
	FindByLastNameAndInitials(ctx context.Context, ti *Teacher) (*Teacher, error)
	FindById(ctx context.Context, id int) (Teacher, error)
	FindByCode(ctx context.Context, code string) (Teacher, error)
	UpdateTgId(ctx context.Context, teacher Teacher) error
	Delete(ctx context.Context, id string) error
}
