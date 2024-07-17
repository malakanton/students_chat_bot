package gglapi

import (
	"context"
	"google.golang.org/api/option"
	"google.golang.org/api/sheets/v4"
	"log"
)

func NewGglApiClient(serviceAccountKey string) (*sheets.Service, error) {
	ctx := context.Background()

	srv, err := sheets.NewService(ctx, option.WithCredentialsFile(serviceAccountKey))
	if err != nil {
		log.Fatalf("Unable to create Sheets service: %v", err)
		return nil, err
	}
	return srv, nil
}
