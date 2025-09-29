package pipeline

import (
	"os"
	"path/filepath"
	"testing"
)

func TestExtractTextFromPDF(t *testing.T) {
	// Get the current working directory.
	wd, err := os.Getwd()
	if err != nil {
		t.Fatalf("os.Getwd() failed: %v", err)
	}

	// Construct the absolute path to the dummy PDF file.
	path := filepath.Join(wd, "testdata", "dummy.pdf")

	// The expected text content of the dummy PDF file.
	expected := "Dummy PDF file"

	// Call the function to extract the text from the PDF.
	actual, err := ExtractTextFromPDF(path)
	if err != nil {
		t.Fatalf("ExtractTextFromPDF failed: %v", err)
	}

	// Compare the actual text with the expected text.
	if actual != expected {
		t.Errorf("ExtractTextFromPDF returned incorrect text. Got: %q, Want: %q", actual, expected)
	}
}
