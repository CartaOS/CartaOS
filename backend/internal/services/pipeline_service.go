package services

import (
	"github.com/CartaOS/CartaOS/backend/internal/pipeline"
)

// PipelineService is a service for the document processing pipeline.
type PipelineService struct{}

// NewPipelineService creates a new PipelineService.
func NewPipelineService() *PipelineService {
	return &PipelineService{}
}

// ProcessDocument extracts text from a PDF document.
func (s *PipelineService) ProcessDocument(path string) (string, error) {
	return pipeline.ExtractTextFromPDF(path)
}
