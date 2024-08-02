package storage

import (
	"context"
	"errors"
	"fmt"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
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

func NewClient(ctx context.Context, dbcfg config.StorageConfig) (conn *pgx.Conn, err error) {
	connString := fmt.Sprintf("postgresql://%s:%s@%s:%s/%s", dbcfg.Username, dbcfg.Password, dbcfg.Host, dbcfg.Port, dbcfg.Database)
	if dbcfg.Attempts < 1 {
		err = errors.New("attempts to connect to db are not passed")
		return nil, err
	}
	err = utils.DoWithTries(func() error {
		ctx, cancel := context.WithTimeout(ctx, 5*time.Second)

		defer cancel()
		conn, err = pgx.Connect(ctx, connString)
		if err != nil {
			return err
		}
		return nil
	}, dbcfg.Attempts, 5*time.Second)

	if err != nil {
		log.Fatalf("Failed to connect to db: %s", err)
	}

	return conn, err

}
