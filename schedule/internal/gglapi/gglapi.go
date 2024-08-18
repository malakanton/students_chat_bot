package gglapi

import (
	"context"
	"google.golang.org/api/drive/v3"
	"google.golang.org/api/option"
	"google.golang.org/api/sheets/v4"
	"log"
)

type GoogleApi struct {
	SheetsService *sheets.Service
	DriveService  *drive.Service
}

func NewGoogleApi(serviceAccountKey string) (*GoogleApi, error) {
	sheetsService, err := NewSheetsClient(serviceAccountKey)
	if err != nil {
		return nil, err
	}
	driveService, err := NewDriveClient(serviceAccountKey)
	if err != nil {
		return nil, err
	}
	newService := GoogleApi{
		SheetsService: sheetsService,
		DriveService:  driveService,
	}
	return &newService, nil
}

func NewSheetsClient(serviceAccountKey string) (*sheets.Service, error) {
	ctx := context.Background()

	srv, err := sheets.NewService(ctx, option.WithCredentialsFile(serviceAccountKey))
	if err != nil {
		log.Fatalf("Unable to create Sheets service: %v", err)
		return nil, err
	}
	return srv, nil
}

func NewDriveClient(serviceAccountKey string) (*drive.Service, error) {
	ctx := context.Background()

	srv, err := drive.NewService(ctx, option.WithCredentialsFile(serviceAccountKey))
	if err != nil {
		log.Fatalf("Unable to create Sheets service: %v", err)
		return nil, err
	}
	return srv, nil
}
