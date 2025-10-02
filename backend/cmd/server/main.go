package main

import (
	"context"
	"errors"
	"log"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"

	customhttp "github.com/CartaOS/CartaOS/backend/internal/server/http"
	"github.com/CartaOS/CartaOS/backend/internal/services"
)

func main() {
	// Define the allowed base directory for PDF processing.
	// Check for environment variable first, then default to testdata directory.
	allowedBaseDir := os.Getenv("PDF_PROCESSING_BASE_DIR")
	if allowedBaseDir == "" {
		allowedBaseDir = "./internal/pipeline/testdata" // Relative to the backend directory
		log.Println("Using default PDF processing base directory: ./internal/pipeline/testdata")
	} else {
		log.Printf("Using environment-configured PDF processing base directory: %s", allowedBaseDir)
	}

	// Server port configuration
	serverPort := os.Getenv("SERVER_PORT")
	if serverPort == "" {
		serverPort = ":8081" // Default to 8081 for the feature branch
		log.Println("Using default server port: 8081")
	} else {
		// Validate server port format
		if !strings.HasPrefix(serverPort, ":") {
			// If the port doesn't start with :, add it
			if serverPort[0] >= '0' && serverPort[0] <= '9' {
				serverPort = ":" + serverPort
			}
		}
		log.Printf("Using environment-configured server port: %s", serverPort)
	}

	// Create the pipeline service and handler
	pipelineService := services.NewPipelineService()
	pipelineHandler := customhttp.NewPipelineHandler(pipelineService, allowedBaseDir)

	mux := http.NewServeMux()
	mux.HandleFunc("/healthz", func(w http.ResponseWriter, r *http.Request) {
		if r.Method != http.MethodGet {
			http.Error(w, http.StatusText(http.StatusMethodNotAllowed), http.StatusMethodNotAllowed)
			return
		}
		w.WriteHeader(http.StatusOK)
		if _, err := w.Write([]byte("OK")); err != nil {
			log.Printf("Error writing health check response: %v", err)
		}
	})
	mux.Handle("/process", pipelineHandler)

	server := &http.Server{
		Addr:         serverPort,
		Handler:      mux,
		ReadTimeout:  5 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	// Run server in a goroutine so it doesn't block.
	go func() {
		log.Printf("Server listening on %s", serverPort)
		if err := server.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			log.Fatalf("Error starting server: %v", err)
		}
	}()

	// Wait for interrupt signal to gracefully shutdown the server.
	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop

	log.Println("Shutting down server...")

	// Give existing requests 5 seconds to finish.
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	if err := server.Shutdown(ctx); err != nil {
		log.Fatalf("Server shutdown failed: %v", err)
	}

	log.Println("Server gracefully stopped")
}
