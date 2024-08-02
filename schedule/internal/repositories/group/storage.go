package group

import "context"

type Repository interface {
	Create(ctx context.Context, group *Group) error
	FindAll(ctx context.Context) (g []Group, err error)
	FindOne(ctx context.Context, id string) (*Group, error)
	Update(ctx context.Context, group Group) error
	Delete(ctx context.Context, id string) error
}
