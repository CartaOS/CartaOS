# CartaOS Documentation Assets

This directory contains visual assets for the CartaOS documentation.

## Screenshot Placeholders

The following screenshot files are referenced in the main README.md but need to be captured from the actual running application:

### Required Screenshots

1. **main-interface.png** - Main CartaOS interface showing Pipeline view
2. **pipeline-view.png** - Document queue with processing controls
3. **settings-view.png** - API key and vault path configuration
4. **lab-view.png** - Document analysis workspace
5. **summaries-view.png** - AI-generated summaries display
6. **workflow-diagram.png** - Visual workflow representation

### Capturing Screenshots

To capture these screenshots:

1. **Build and run CartaOS**:
   ```bash
   cd frontend && npm run build
   cd ../src-tauri && cargo tauri dev
   ```

2. **Navigate through each view** and capture screenshots at appropriate resolutions (1200x800 recommended)

3. **Save screenshots** in this directory with the exact filenames referenced in README.md

### Image Specifications

- **Format**: PNG (preferred) or JPG
- **Resolution**: 1200x800 pixels minimum
- **Quality**: High quality, clear text and UI elements
- **Content**: Show realistic but anonymized data where applicable

### Optional Assets

- **banner.png** - Header banner for README (1200x300 recommended)
- **logo.png** - CartaOS logo in various sizes
- **icon.png** - Application icon

## Notes

These placeholder references ensure the documentation structure is complete even before screenshots are captured. The actual screenshot files should be added when the application is ready for demonstration.
