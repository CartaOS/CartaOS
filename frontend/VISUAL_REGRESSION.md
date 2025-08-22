# Visual Regression Testing Guide

This document describes the visual regression testing setup for CartaOS frontend using Playwright's built-in screenshot comparison.

## Overview

We use Playwright's native screenshot comparison for visual regression testing instead of Storybook + Chromatic to avoid complex dependency conflicts while still providing comprehensive visual protection for key components.

## Running Visual Tests

### Generate Initial Screenshots

```bash
# Generate baseline screenshots for the first time
npm run visual:update

# This creates reference screenshots in test-results/
```

### Run Visual Regression Tests

```bash
# Run visual regression tests against baselines
npm run visual:test

# Tests will fail if any visual changes are detected
```

### Update Screenshots After Intentional Changes

```bash
# Update baseline screenshots after UI changes
npm run visual:update

# Only run this when visual changes are intentional
```

## Test Coverage

### Components Tested

1. **ActionButton** - All color variants and states (normal, enabled, loading)
2. **QueueColumn** - Empty states for all pipeline queues (Triage, OCR, Lab)
3. **LogPanel** - Status message area and log display
4. **Navigation Tabs** - Active states for all views (Pipeline, Lab, Summaries, Settings)
5. **Form Components** - Settings form in various states (initial, filled, validation)

### Visual Scenarios

- **Component States**: Normal, loading, error, validation states
- **Responsive Design**: Desktop (1280x720), tablet (768x1024), mobile (375x667)
- **Color Consistency**: Theme colors across different components
- **Layout Integrity**: Proper spacing, alignment, and visual hierarchy

## Screenshot Organization

Screenshots are stored in `test-results/visual-regression-*` directories:

```
test-results/
├── visual-regression-ActionButton-component-visual-states-chromium/
│   ├── action-button-normal.png
│   ├── action-button-enabled.png
│   └── action-button-loading.png
├── visual-regression-QueueColumn-component-visual-states-chromium/
│   ├── queue-columns-empty.png
│   ├── triage-queue-empty.png
│   └── ocr-queue-empty.png
└── ...
```

## CI Integration

### GitHub Actions

Add to `.github/workflows/frontend-tests.yml`:

```yaml
- name: Run Visual Regression Tests
  run: |
    cd frontend
    npm run visual:test
    
- name: Upload Visual Diff Artifacts
  if: failure()
  uses: actions/upload-artifact@v3
  with:
    name: visual-diffs
    path: frontend/test-results/
```

### Pull Request Workflow

1. **Developer makes UI changes**
2. **CI runs visual tests** - fails if screenshots differ
3. **Developer reviews diffs** in test-results/
4. **If changes are intentional**: run `npm run visual:update` and commit new baselines
5. **If changes are bugs**: fix the UI and re-run tests

## Best Practices

### When to Update Baselines

✅ **Update baselines when**:
- Intentional UI design changes
- New features with visual components
- Accessibility improvements that affect appearance
- Color scheme or theme updates

❌ **Don't update baselines for**:
- Unintentional visual regressions
- Broken layouts or styling bugs
- Inconsistent component behavior

### Screenshot Quality

- **Consistent viewport sizes** for reliable comparisons
- **Wait for elements to load** before capturing
- **Stable test data** to avoid flaky visual tests
- **Focus on key components** rather than entire pages

### Debugging Visual Failures

1. **Check test-results/** for actual vs expected screenshots
2. **Look for diff images** showing highlighted changes
3. **Run tests locally** to reproduce issues
4. **Use browser dev tools** to inspect styling changes

## Troubleshooting

### Common Issues

1. **Flaky screenshots**: Ensure elements are fully loaded before capture
2. **Font rendering differences**: Use consistent test environments
3. **Animation timing**: Add waits or disable animations in tests
4. **Browser differences**: Stick to single browser (Chromium) for consistency

### Performance Considerations

- Visual tests are slower than unit tests
- Run on key components only, not every UI element
- Use in CI but consider running subset in development
- Balance coverage vs execution time

## Integration with Other Tests

Visual regression tests complement:
- **Unit tests**: Component logic and behavior
- **E2E tests**: User workflows and interactions
- **Accessibility tests**: WCAG compliance
- **Performance tests**: Load times and responsiveness

## Monitoring

- Track visual test execution time
- Monitor false positive rates
- Review screenshot storage usage
- Set up alerts for consistent failures

This approach provides robust visual regression protection without the complexity of full Storybook setup, making it easier to maintain and integrate into the development workflow.
