# Sources and verification

Use this file when sources disagree, a claim needs a citation, or the current
verification boundary matters.

## Curated snapshot

This skill was reviewed against Apple's published Liquid Glass guidance and API
documentation on 14 August 2026. It intentionally covers the APIs, design
decisions, and migration issues most useful in real projects rather than trying
to mirror every Apple page. Treat OS 27 beta details as a snapshot and verify a
specific declaration when the active SDK or task makes it consequential.

## Source precedence

Resolve conflicts in this order:

1. Current Apple API documentation for names, declarations, and availability.
2. Current Apple Human Interface Guidelines for design rules.
3. The newest relevant WWDC session or Group Lab.
4. Current Apple sample code.
5. Apple's Xcode agent skills exported from the same Xcode version in use.
6. Current Apple Developer Forums answers from identifiable Apple staff, as
   clarification rather than a substitute for documentation.
7. Older Apple sessions.
8. Reproducible community implementations.

Do not take an API identifier from a transcript without checking its API page.
Transcripts can flatten punctuation or attach a modifier to the wrong type.

Two verified examples:

| Session wording | Documented API |
|---|---|
| `.toolbarMinimizeBehavior(_:for:)` | `toolbarMinimizationBehavior(_:for:)` in OS 27 beta |
| `visibilityPriority` on a view | `ToolbarContent.visibilityPriority(_:)` |

## Version routing

WWDC25 introduced the OS 26 design. WWDC26 covers the current OS 27 betas.
Keep both rule sets and route by build SDK, platform, and deployment target.

API pages currently mark OS 27 availability as beta. Preserve those beta labels
until the API documentation for the active Xcode toolchain says otherwise.

## Verification boundary

- Verify API names, declarations, and availability against current Apple API
  documentation before writing code.
- Treat code samples as fragments. Build them in the owning project with its
  selected Xcode version and deployment targets.
- Use HIG and session guidance for design decisions, not as substitutes for API
  declarations.
- Use community material to reproduce edge cases. Do not let it override Apple
  documentation.
- Export Apple's Xcode agent skills from the installed Xcode when available and
  prefer matching-version guidance where it overlaps this skill.

## Apple documentation endpoints

Apple's documentation pages are rendered client-side. For exact declarations
and availability, read the underlying JSON:

```text
https://developer.apple.com/tutorials/data/documentation/<path>.json
https://developer.apple.com/tutorials/data/design/human-interface-guidelines/<page>.json
```

WWDC sessions use:

```text
https://developer.apple.com/videos/play/wwdc<year>/<session>/
```

Read `metadata.platforms` for availability. Use the declaration tokens in the
page content for signatures. Do not infer cross-platform availability from an
iOS declaration or a WWDC slide.

## Exported Xcode skills

On a Mac with the target Xcode selected, run:

```bash
xcrun agent skills export
```

Record the Xcode version with the export. Re-export after an Xcode update, and
prefer current API documentation if an exported skill and an API page disagree.
