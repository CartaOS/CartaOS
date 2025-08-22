# Performance Testing Guide

This document describes the performance testing setup for CartaOS frontend.

## Overview

We use two complementary approaches for performance testing:

1. **Lighthouse CI** - Comprehensive performance audits with Core Web Vitals
2. **Playwright Performance Tests** - Fast timing assertions for key interactions

## Running Performance Tests

### Lighthouse CI

```bash
# Run full Lighthouse audit with thresholds
npm run perf

# This will:
# 1. Build the production app
# 2. Start preview server
# 3. Run Lighthouse audits on key pages
# 4. Generate performance report
# 5. Exit with success/failure based on thresholds
```

### Playwright Performance Tests

```bash
# Run fast performance timing tests
npm run perf:e2e

# This runs performance.spec.ts with timing assertions
```

## Performance Thresholds

### Lighthouse Thresholds (0-100 scale)

- **Performance**: ≥75 - Core Web Vitals, load times, resource optimization
- **Accessibility**: ≥90 - WCAG compliance, screen reader support
- **Best Practices**: ≥80 - Security, modern web standards
- **SEO**: ≥80 - Search engine optimization
- **PWA**: ≥50 - Progressive Web App features (lower priority)

### Playwright Timing Thresholds

- **Page Load**: <3000ms - Initial page load time
- **Navigation**: <1000ms - View switching between Pipeline/Lab/Settings/Summaries
- **Form Input**: <500ms - Form field responsiveness
- **Button Response**: <2000ms - Action button processing time
- **Core Web Vitals**:
  - First Contentful Paint (FCP): <2000ms
  - Largest Contentful Paint (LCP): <4000ms
  - DOM Content Loaded: <3000ms
  - Total Load Time: <5000ms

## Pages Tested

1. **Home Page** (`/`) - Main pipeline interface
2. **Settings Page** (`/?view=settings`) - Configuration form

## CI Integration

### GitHub Actions

Add to `.github/workflows/frontend-tests.yml`:

```yaml
- name: Run Performance Tests
  run: |
    cd frontend
    npm run perf:e2e
    
- name: Run Lighthouse CI (nightly)
  if: github.event_name == 'schedule'
  run: |
    cd frontend
    npm run perf
```

### Local Development

```bash
# Quick performance check during development
npm run perf:e2e

# Full audit before releases
npm run perf
```

## Interpreting Results

### Lighthouse Results

- Results saved to `lighthouse-results.json`
- Console output shows pass/fail for each threshold
- Detailed metrics available in JSON report

### Playwright Results

- Console output shows actual timing measurements
- Tests fail if any threshold is exceeded
- Useful for catching performance regressions during development

## Troubleshooting

### Common Issues

1. **Server not ready**: Increase sleep time in `perf` script if Lighthouse fails to connect
2. **Flaky timing tests**: Network conditions can affect results; run multiple times
3. **Threshold too strict**: Adjust thresholds based on target device performance

### Performance Optimization Tips

1. **Bundle size**: Monitor JavaScript bundle size in build output
2. **Image optimization**: Ensure images are properly sized and compressed
3. **Code splitting**: Use dynamic imports for non-critical code
4. **Caching**: Leverage browser caching for static assets

## Monitoring

- Run `npm run perf:e2e` on every PR
- Run `npm run perf` nightly or before releases
- Track performance trends over time
- Set up alerts for threshold violations in CI

## Updating Thresholds

Thresholds are defined in:
- `scripts/lighthouse-ci.mjs` - Lighthouse thresholds
- `e2e/performance.spec.ts` - Playwright timing thresholds

Adjust based on:
- Target device performance (mobile vs desktop)
- User experience requirements
- Technical constraints
- Performance budget decisions
