// Local types to integrate jest-axe with Vitest for svelte-check
// Duplicates tests/axe.d.ts so editors and svelte-check pick it up from src

declare module 'jest-axe' {
	export interface AxeResults {
		violations: unknown[];
	}
	export function axe(
		container?: Element | Document | DocumentFragment,
		options?: unknown
	): Promise<AxeResults>;
	export function toHaveNoViolations(...args: unknown[]): unknown;
}

declare module 'vitest' {
	interface Assertion {
		toHaveNoViolations(): void;
	}
}

export {};
