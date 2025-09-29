package http

import (
	"encoding/json"
	"net/http"
	"path/filepath"
	"strings"
	"fmt"

	"github.com/CartaOS/CartaOS/backend/internal/services"
)

// PipelineHandler is a handler for the document processing pipeline.
type PipelineHandler struct {
	service *services.PipelineService
	allowedBaseDir string
}

// NewPipelineHandler creates a new PipelineHandler.
func NewPipelineHandler(service *services.PipelineService, allowedBaseDir string) *PipelineHandler {
	return &PipelineHandler{service: service, allowedBaseDir: allowedBaseDir}
}

type processRequest struct {
	Path string `json:"path"`
}

type processResponse struct {
	Text string `json:"text"`
}

func (h *PipelineHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, http.StatusText(http.StatusMethodNotAllowed), http.StatusMethodNotAllowed)
		return
	}

	var req processRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		http.Error(w, "Invalid request payload", http.StatusBadRequest)
		return
	}

	// --- Input Validation and Path Restriction ---
	if req.Path == "" {
		http.Error(w, "File path cannot be empty", http.StatusBadRequest)
		return
	}

	// Clean the path to remove any ../ or ./ sequences
	cleanPath := filepath.Clean(req.Path)

	// Check for directory traversal attempts
	if strings.Contains(cleanPath, "..") || strings.HasPrefix(cleanPath, "/") || strings.HasPrefix(cleanPath, "~") {
		http.Error(w, "Invalid file path provided", http.StatusBadRequest)
		return
	}

	// Construct the full absolute path
	fullPath := filepath.Join(h.allowedBaseDir, cleanPath)

	// Ensure the resolved path is within the allowed base directory
	// This is a critical step to prevent path traversal
	resolvedPath, err := filepath.Abs(fullPath)
	if err != nil {
		http.Error(w, "Error resolving file path", http.StatusInternalServerError)
		return
	}
	allowedBaseDirAbs, err := filepath.Abs(h.allowedBaseDir)
	if err != nil {
		http.Error(w, "Server configuration error", http.StatusInternalServerError)
		return
	}

	if !strings.HasPrefix(resolvedPath, allowedBaseDirAbs) {
		http.Error(w, "Access denied: file outside allowed directory", http.StatusForbidden)
		return
	}
	// --- End Input Validation and Path Restriction ---


	text, err := h.service.ProcessDocument(resolvedPath)
	if err != nil {
		// Log the actual error for debugging, but return a generic error to the client
		fmt.Printf("Error processing document %s: %v\n", resolvedPath, err)
		http.Error(w, "Error processing document", http.StatusInternalServerError)
		return
	}

	resp := processResponse{Text: text}
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(resp); err != nil {
		fmt.Printf("Error encoding response: %v\n", err)
		http.Error(w, "Error generating response", http.StatusInternalServerError)
		return
	}
}
