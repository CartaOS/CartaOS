#!/usr/bin/env node

/**
 * Lighthouse CI script for performance testing
 * Runs Lighthouse audits on key pages and enforces performance thresholds
 */

import lighthouse from 'lighthouse';
import chromeLauncher from 'chrome-launcher';
import fs from 'fs';
import path from 'path';

// Performance thresholds (0-100 scale)
const THRESHOLDS = {
  performance: 75,
  accessibility: 90,
  'best-practices': 80,
  seo: 80,
  pwa: 50 // Lower threshold for PWA as it's not the main focus
};

// Pages to test
const PAGES = [
  { name: 'Home', url: 'http://127.0.0.1:4173/' },
  { name: 'Settings', url: 'http://127.0.0.1:4173/?view=settings' }
];

async function runLighthouse(url, options = {}) {
  const chrome = await chromeLauncher.launch({ chromeFlags: ['--headless'] });
  
  const runnerResult = await lighthouse(url, {
    ...options,
    port: chrome.port,
  });

  await chrome.kill();
  return runnerResult;
}

async function main() {
  console.log('🚀 Starting Lighthouse CI performance checks...\n');
  
  const results = [];
  let allPassed = true;

  for (const page of PAGES) {
    console.log(`📊 Testing ${page.name}: ${page.url}`);
    
    try {
      const result = await runLighthouse(page.url);
      const scores = result.lhr.categories;
      
      console.log(`\n📈 ${page.name} Results:`);
      
      // Check each category against thresholds
      for (const [category, threshold] of Object.entries(THRESHOLDS)) {
        const score = Math.round(scores[category].score * 100);
        const passed = score >= threshold;
        const status = passed ? '✅' : '❌';
        
        console.log(`  ${status} ${category}: ${score}/100 (threshold: ${threshold})`);
        
        if (!passed) {
          allPassed = false;
        }
      }
      
      results.push({
        page: page.name,
        url: page.url,
        scores: Object.fromEntries(
          Object.entries(scores).map(([key, value]) => [key, Math.round(value.score * 100)])
        ),
        passed: Object.entries(THRESHOLDS).every(([category, threshold]) => 
          Math.round(scores[category].score * 100) >= threshold
        )
      });
      
    } catch (error) {
      console.error(`❌ Error testing ${page.name}:`, error.message);
      allPassed = false;
    }
    
    console.log(''); // Empty line for readability
  }

  // Generate summary report
  console.log('📋 Summary Report:');
  console.log('==================');
  
  results.forEach(result => {
    const status = result.passed ? '✅ PASS' : '❌ FAIL';
    console.log(`${status} ${result.page}`);
    Object.entries(result.scores).forEach(([category, score]) => {
      console.log(`  - ${category}: ${score}/100`);
    });
  });

  // Save detailed results to file
  const reportPath = path.join(process.cwd(), 'lighthouse-results.json');
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2));
  console.log(`\n📄 Detailed results saved to: ${reportPath}`);

  // Exit with appropriate code
  if (allPassed) {
    console.log('\n🎉 All performance checks passed!');
    process.exit(0);
  } else {
    console.log('\n💥 Some performance checks failed. See results above.');
    process.exit(1);
  }
}

// Handle CLI execution
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    console.error('💥 Lighthouse CI failed:', error);
    process.exit(1);
  });
}

export { runLighthouse, THRESHOLDS, PAGES };
