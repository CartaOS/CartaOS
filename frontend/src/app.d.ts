// See https://svelte.dev/docs/kit/types#app.d.ts
// for information about these interfaces
declare global {
	namespace App {
		// interface Error {}
		// interface Locals {}
		// interface PageData {}
		// interface PageState {}
		// interface Platform {}
	}
}

// Allow importing SVG assets (e.g., favicon.svg)
declare module '*.svg' {
  const src: string;
  export default src;
}

export {};
