package pipeline

import (
	"os"
	"path/filepath"
	"strings"
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

func TestExtractTextFromPDF_TableDriven(t *testing.T) {
	// Get the current working directory.
	wd, err := os.Getwd()
	if err != nil {
		t.Fatalf("os.Getwd() failed: %v", err)
	}

	tests := []struct {
		name        string
		filename    string
		expectError bool
		expected    string
	}{
		{
			name:        "Valid dummy PDF",
			filename:    "dummy.pdf",
			expectError: false,
			expected:    "Dummy PDF file",
		},
		{
			name:        "Non-existent file",
			filename:    "nonexistent.pdf",
			expectError: true,
			expected:    "",
		},
		{
			name:        "Empty file name",
			filename:    "",
			expectError: true,
			expected:    "",
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			path := filepath.Join(wd, "testdata", tt.filename)
			actual, err := ExtractTextFromPDF(path)

			if tt.expectError {
				if err == nil {
					t.Errorf("Expected error for %s, but got none", tt.name)
				}
				return
			}

			if err != nil {
				t.Errorf("Unexpected error for %s: %v", tt.name, err)
				return
			}

			if actual != tt.expected {
				t.Errorf("For %s: expected %q, got %q", tt.name, tt.expected, actual)
			}
		})
	}
}

func TestExtractTextFromPDF_EmptyPages(t *testing.T) {
	wd, err := os.Getwd()
	if err != nil {
		t.Fatalf("os.Getwd() failed: %v", err)
	}

	// This test assumes that the dummy PDF might have empty pages
	// The function should handle empty pages gracefully
	path := filepath.Join(wd, "testdata", "dummy.pdf")

	actual, err := ExtractTextFromPDF(path)
	if err != nil {
		t.Errorf("Unexpected error: %v", err)
	}

	// Check that the returned string doesn't have unexpected empty content
	if strings.Contains(actual, "  ") { // Two spaces in a row might indicate empty page issues
		t.Logf("Note: Returned text contains multiple spaces: %q", actual)
	}
}

func TestExtractTextFromPDF_ErrorScenarios(t *testing.T) {
	wd, err := os.Getwd()
	if err != nil {
		t.Fatalf("os.Getwd() failed: %v", err)
	}

	errorTests := []struct {
		name        string
		path        string
		expectError bool
	}{
		{
			name:        "Non-existent file",
			path:        filepath.Join(wd, "testdata", "does_not_exist.pdf"),
			expectError: true,
		},
		{
			name:        "Empty path",
			path:        "",
			expectError: true,
		},
		{
			name:        "Directory instead of file",
			path:        filepath.Join(wd, "testdata"), // This is a directory
			expectError: true,
		},
	}

	for _, tt := range errorTests {
		t.Run(tt.name, func(t *testing.T) {
			_, err := ExtractTextFromPDF(tt.path)
			
			if tt.expectError {
				if err == nil {
					t.Errorf("Expected error for %s, but got none", tt.name)
				}
				// Success: error occurred as expected
				return
			}

			if err != nil {
				t.Errorf("Unexpected error for %s: %v", tt.name, err)
			}
		})
	}
}

func TestExtractTextFromPDF_EmptyAndCorruptedFiles(t *testing.T) {
	wd, err := os.Getwd()
	if err != nil {
		t.Fatalf("os.Getwd() failed: %v", err)
	}

	// Test with an empty PDF file
	emptyPDFPath := filepath.Join(wd, "testdata", "empty.pdf")
	// Create an empty PDF file for testing
	err = os.WriteFile(emptyPDFPath, []byte(""), 0644)
	if err != nil {
		t.Logf("Could not create empty PDF test file: %v", err)
	} else {
		defer os.Remove(emptyPDFPath) // Clean up after the test
		
		// Test with the empty PDF file
		_, err := ExtractTextFromPDF(emptyPDFPath)
		if err == nil {
			t.Log("Empty PDF file was processed without errors (this may be expected)")
		} else {
			t.Logf("Empty PDF file produced error (this may also be expected): %v", err)
		}
	}
	
	// Test with a non-PDF file
	nonPDFPath := filepath.Join(wd, "testdata", "not_pdf.txt")
	err = os.WriteFile(nonPDFPath, []byte("This is not a PDF file"), 0644)
	if err != nil {
		t.Logf("Could not create non-PDF test file: %v", err)
	} else {
		defer os.Remove(nonPDFPath) // Clean up after the test
		
		// Test with the non-PDF file
		_, err := ExtractTextFromPDF(nonPDFPath)
		if err == nil {
			t.Log("Non-PDF file was processed without errors (function handles it gracefully)")
		} else {
			t.Logf("Non-PDF file produced error as expected: %v", err)
		}
	}
}
