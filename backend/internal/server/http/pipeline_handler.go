package http

import (
	"encoding/json"
	"net/http"

	"github.com/CartaOS/CartaOS/backend/internal/services"
)

// PipelineHandler is a handler for the document processing pipeline.
type PipelineHandler struct {
	service *services.PipelineService
}

// NewPipelineHandler creates a new PipelineHandler.
func NewPipelineHandler(service *services.PipelineService) *PipelineHandler {
	return &PipelineHandler{service: service}
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
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	text, err := h.service.ProcessDocument(req.Path)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	resp := processResponse{Text: text}
	w.Header().Set("Content-Type", "application/json")
	if err := json.NewEncoder(w).Encode(resp); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
}