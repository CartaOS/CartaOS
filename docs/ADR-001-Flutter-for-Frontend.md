# ADR-001: Flutter for Cross-Platform Frontend

*   **Status:** Superseded
*   **Date:** 2025-09-28

---

## Superseded by ADR-002

This decision was superseded by [ADR-002: Strategic Pivot to Python Backend and Tauri/Svelte Frontend](./ADR-002-Pivo-Tecnologico-Python-Tauri.md) on 2025-10-02.

**Reasoning for Invalidation:** While Flutter remains a strong choice for cross-platform development including mobile, a re-evaluation concluded that the Tauri/Svelte/TailwindCSS stack is better aligned with the immediate MVP goal of creating a lightweight, high-performance desktop application. The key advantages of the new stack, such as significantly smaller binary sizes and direct access to the web ecosystem for document and text-heavy UI components, were deemed critical for the initial product's success. Please refer to ADR-002 for a detailed justification.

---

*The original text of the ADR is preserved below for historical context.*

## Original Context

The product vision for CartaOS v2 requires a presence on multiple platforms: Desktop (Windows, macOS, Linux), Web, and Mobile (iOS, Android). Maintaining separate native codebases for each of these platforms (e.g., Swift/SwiftUI for iOS/macOS, Kotlin/Compose for Android, C#/.NET for Windows, and a web framework like React/Svelte) is logistically complex and financially unfeasible for a lean team.

This would create a massive development overhead, make it difficult to maintain feature parity across platforms, and drastically increase the time-to-market for new features. We need a solution that allows us to reach all target platforms with a single codebase, without significantly compromising performance or user experience.

## Original Decision

We decided to adopt the **Flutter** framework, using the **Dart** language, as the primary technology for the development of the entire client interface (frontend) of CartaOS v2.

## Original Justification

The choice of Flutter was based on four main pillars:

1.  **Single Codebase and True Cross-Platform Capability:** Flutter allows development and compilation for all our six target platforms (Windows, macOS, Linux, Web, iOS, Android) from a single repository and codebase. This is its most significant strategic advantage, as it maximizes development efficiency.

2.  **Native Performance:** Unlike solutions based on web wrappers (like Electron), Flutter does not bundle a browser. It compiles Dart code to native machine code (ARM, x86) and uses its own high-performance rendering engine (Skia) to draw the UI directly on the screen. This results in applications with fast startup, smooth animations at 60/120fps, and a native feel of responsiveness.

3.  **Consistent and Controlled UI:** As Flutter controls every pixel on the screen, it ensures that the user interface, design system, and user experience are virtually identical across all platforms. This strengthens the CartaOS brand identity and reduces the time spent on platform-specific CSS or layout adjustments.

4.  **Strong Ecosystem and Google Support:** Flutter is an open-source project backed by Google, with a large, active, and growing community. The `pub.dev` package repository is vast and mature, offering ready-made solutions for most common challenges (state management, secure storage, network communication, etc.), which accelerates development.

### Alternatives Considered (at the time)

*   **Tauri/Svelte:** While excellent for lightweight desktop applications, expanding to mobile would require a complete rewrite in another framework (like React Native or native). Maintaining parity between the web/desktop version and the mobile version would be a challenge.
*   **React Native:** Strong on mobile, but its desktop support is still less mature and more fragmented than Flutter's. Performance, especially in complex applications, may not be as consistent as Flutter's.
*   **Separate Native Development:** Rejected as unfeasible in terms of cost, time, and team size.

## Original Consequences

*   **Positive:**
    *   Drastic reduction in development and maintenance time and cost.
    *   Unified frontend team, focused on a single stack (Dart/Flutter).
    *   Faster rollout of features across all platforms simultaneously.
    *   Consistent user experience that strengthens the product brand.

*   **Negative or Risks to Mitigate:**
    *   **Learning Curve:** The development team would need to have or acquire proficiency in Dart and Flutter architecture (e.g., state management with BLoC/Riverpod).
    *   **Application Size:** The final size of a Flutter application ("Hello World") is larger than that of a fully native application, due to the inclusion of the rendering engine. However, for a complex application like CartaOS, this difference becomes proportionally less significant.
    *   **Specific Native Integrations:** For features that depend on low-level OS APIs, it would be necessary to develop "Platform Channels," which adds a layer of complexity. This was to be mapped and planned for features like invoking local scripts in the free mode.