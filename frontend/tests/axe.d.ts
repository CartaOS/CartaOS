// Type declarations to integrate jest-axe with Vitest
// Keep comments in English per project guidelines.

declare module 'jest-axe' {
  export interface AxeResults {
    violations: unknown[];
  }
  // Minimal typing surface for our usage
  export function axe(container?: Element | Document | DocumentFragment, options?: unknown): Promise<AxeResults>;
}

// Add custom matcher type for Vitest
declare global {
  // Vitest's assertion namespace
  namespace Vi {
    interface Assertion {
      toHaveNoViolations(): void;
    }
  }
}

export {};
