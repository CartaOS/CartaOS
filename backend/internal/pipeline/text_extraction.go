package pipeline

import (
	"bytes"
	"os"
	"strings"

	"github.com/ledongthuc/pdf"
)

// ExtractTextFromPDF extracts text from a native PDF file.
func ExtractTextFromPDF(path string) (string, error) {
	// Open the PDF file
	file, err := os.Open(path)
	if err != nil {
		return "", err
	}
	defer file.Close()

	// Get file info to determine file size
	fileInfo, err := file.Stat()
	if err != nil {
		return "", err
	}

	// Create a new PDF reader
	pdfReader, err := pdf.NewReader(file, fileInfo.Size())
	if err != nil {
		return "", err
	}

	var buf bytes.Buffer

	// Extract text from each page
	totalPages := pdfReader.NumPage()
	for i := 1; i <= totalPages; i++ {
		page := pdfReader.Page(i)

		// Extract plain text from the page
		// Try to get the fonts for the page first
		fonts, err := getFontsForPage(pdfReader, i)
		var pageText string
		if err != nil {
			// If we can't get fonts, try without fonts
			pageText, err = page.GetPlainText(nil)
		} else {
			pageText, err = page.GetPlainText(fonts)
		}

		if err != nil {
			continue // Skip pages that can't be read
		}
		buf.WriteString(pageText)
	}

	return strings.TrimSpace(buf.String()), nil
}

// getFontsForPage gets the fonts for a specific page
func getFontsForPage(reader *pdf.Reader, pageNum int) (map[string]*pdf.Font, error) {
	page := reader.Page(pageNum)
	fonts := page.Fonts()
	fontMap := make(map[string]*pdf.Font)
	for _, fontName := range fonts {
		font := page.Font(fontName)
		fontMap[fontName] = &font
	}
	return fontMap, nil
}
