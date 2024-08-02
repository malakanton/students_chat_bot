package config

import (
	"log"
	"os"
	"time"

	"github.com/ilyakaznacheev/cleanenv"
)

type Config struct {
	Env          string `yaml:"env" env-default:"dev"`
	StoragePath  string `yaml:"storage_path"`
	GoogleConfig `yaml:"google_config"`
	HttpServer   `yaml:"http_server"`
	Storage      StorageConfig `yaml:"storage"`
	Settings     Settings      `yaml:"settings"`
}

type Settings struct {
	TeacherCodeSize int `yaml:"teacher_code_size"`
}

type GoogleConfig struct {
	GoogleCredsPath string `yaml:"google_creds_path"`
	SpreadSheetId   string `yaml:"spreadsheets_id"`
}

type StorageConfig struct {
	Host     string `json:"host"`
	Port     string `json:"port"`
	Username string `json:"username"`
	Password string `json:"password"`
	Database string `json:"database"`
	Attempts int    `json:"attempts"`
}

type HttpServer struct {
	Address     string        `yaml:"address" env-default:"localhost:8080"`
	Timeout     time.Duration `yaml:"timeout" env-default:"4s"`
	IdleTimeout time.Duration `yaml:"idle_timeout" env-default:"60s"`
}

func MustConfig() *Config {
	configPath := os.Getenv("CONFIG_PATH")

	if configPath == "" {
		log.Fatal("CONFIG_PATH is not set")
	}

	if _, err := os.Stat(configPath); os.IsNotExist(err) {
		log.Fatalf("Config file %s does not exist", configPath)
	}

	var cfg Config

	if err := cleanenv.ReadConfig(configPath, &cfg); err != nil {
		log.Fatalf("Failed to read config file %s", err)
	}
	return &cfg
}
