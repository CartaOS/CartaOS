package pipeline

import (
	"bytes" // Import bytes package
	"os"

	"github.com/dslipak/pdf"
)

// ExtractTextFromPDF extracts text from a native PDF file.
func ExtractTextFromPDF(path string) (string, error) {
	f, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer f.Close()

	fi, err := f.Stat()
	if err != nil {
		return "", err
	}

	r, err := pdf.NewReader(f, fi.Size())
	if err != nil {
		return "", err
	}

	numPages := r.NumPage()
	var buf bytes.Buffer // Use bytes.Buffer for efficient string building
	for i := 1; i <= numPages; i++ {
		p := r.Page(i)
		if p.V.IsNull() {
			continue
		}
		t, err := p.GetPlainText(nil)
		if err != nil {
			return "", err
		}
		buf.WriteString(t) // Write to buffer
	}

	return buf.String(), nil
}
