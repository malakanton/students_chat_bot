package storage

import (
	"context"
	"fmt"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgxpool"
	"log"
	"schedule/internal/config"
	"schedule/pkg/utils"
	"time"
)

type Client interface {
	Exec(ctx context.Context, sql string, arguments ...any) (pgconn.CommandTag, error)
	Query(ctx context.Context, sql string, args ...any) (pgx.Rows, error)
	QueryRow(ctx context.Context, sql string, args ...any) pgx.Row
	Begin(ctx context.Context) (pgx.Tx, error)
}

func NewClient(ctx context.Context, dbcfg config.StorageConfig) (pool *pgxpool.Pool, err error) {
	connString := fmt.Sprintf("postgresql://%s:%s@%s:%s/%s", dbcfg.Username, dbcfg.Password, dbcfg.Host, dbcfg.Port, dbcfg.Database)

	err = utils.DoWithTries(func() error {
		ctx, cancel := context.WithTimeout(ctx, 5*time.Second)

		defer cancel()

		pool, err = pgxpool.New(ctx, connString)
		if err != nil {
			return err
		}
		return nil
	}, dbcfg.Attempts, 5*time.Second)

	if err != nil {
		log.Fatalf("Failed to connect to db: %s", err)
	}

	return pool, err

}
